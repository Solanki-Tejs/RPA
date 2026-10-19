from fastapi import FastAPI, BackgroundTasks, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import subprocess
import os
import sqlite3
import shutil

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            plotify_email TEXT,
            plotify_password TEXT,
            seller_plotify_email TEXT,
            seller_plotify_password TEXT,
            buyer_name TEXT,
            buyer_phone TEXT,
            buyer_budget TEXT,
            buyer_occupation TEXT,
            buyer_moving_date TEXT,
            buyer_message TEXT,
            buyer_identity_doc TEXT,
            buyer_income_doc TEXT,
            buyer_bank_doc TEXT,
            seller_title TEXT,
            seller_price TEXT,
            seller_category TEXT,
            seller_location TEXT,
            seller_description TEXT,
            seller_bedrooms TEXT,
            seller_bathrooms TEXT,
            seller_area TEXT,
            seller_type TEXT,
            seller_owner_name TEXT,
            seller_phone TEXT,
            seller_amenities TEXT,
            seller_map_link TEXT,
            seller_floor TEXT,
            seller_total_floors TEXT,
            seller_furnishing TEXT,
            seller_facing TEXT,
            seller_image_doc TEXT,
            seller_identity_doc TEXT,
            seller_ownership_doc TEXT
        )
    ''')
    columns = [
        "seller_plotify_email TEXT", "seller_plotify_password TEXT",
        "buyer_name TEXT", "buyer_phone TEXT", "buyer_budget TEXT", "buyer_occupation TEXT",
        "buyer_moving_date TEXT", "buyer_message TEXT", "buyer_identity_doc TEXT",
        "buyer_income_doc TEXT", "buyer_bank_doc TEXT",
        "seller_title TEXT", "seller_price TEXT", "seller_category TEXT", "seller_location TEXT",
        "seller_description TEXT", "seller_bedrooms TEXT", "seller_bathrooms TEXT", "seller_area TEXT",
        "seller_type TEXT", "seller_owner_name TEXT", "seller_phone TEXT", "seller_email TEXT", "seller_amenities TEXT",
        "seller_map_link TEXT", "seller_floor TEXT", "seller_total_floors TEXT", "seller_furnishing TEXT",
        "seller_facing TEXT", "seller_image_doc TEXT", "seller_identity_doc TEXT", "seller_ownership_doc TEXT"
    ]
    for col in columns:
        try:
            cursor.execute(f'ALTER TABLE users ADD COLUMN {col}')
        except:
            pass
    conn.commit()
    conn.close()

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    email: str
    password: str

class SettingsRequest(BaseModel):
    user_id: int
    plotify_email: str
    plotify_password: str
    buyer_name: str = ""
    buyer_phone: str = ""
    buyer_budget: str = ""
    buyer_occupation: str = ""
    buyer_moving_date: str = ""
    buyer_message: str = ""
    buyer_identity_doc: str = ""
    buyer_income_doc: str = ""
    buyer_bank_doc: str = ""

# Global state to track bot running status
bot_status = {
    "is_running": False,
    "last_run_status": None, # "success" or "failed"
    "logs": ""
}
current_process = None

def run_robot_bot(req: dict):
    global current_process
    bot_status["is_running"] = True
    bot_status["logs"] = f"Bot started task '{req['task']}' as user '{req['email']}'...\n"
    
    # We will point to specific robot scripts based on the task selected
    script_name = "auto_approve.robot" # Default fallback
    if req["task"] == "auto_approve":
        script_name = "auto_approve.robot"
    elif req["task"] == "export_csv":
        script_name = "auto_export_csv.robot"
    elif req["task"] == "auto_apply":
        script_name = "auto_apply.robot"
    elif req["task"] == "auto_list":
        script_name = "auto_list.robot"
    elif req["task"] == "auto_list_bulk":
        script_name = "auto_list_bulk.robot"
    elif req["task"] == "buyer_export":
        script_name = "buyer_export.robot"

    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", script_name)
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT buyer_name, buyer_phone, buyer_budget, buyer_occupation, buyer_moving_date, buyer_message, buyer_identity_doc, buyer_income_doc, buyer_bank_doc, seller_owner_name, seller_phone, seller_email, seller_identity_doc FROM users WHERE id = ?", (req["user_id"],))
    user_data = cursor.fetchone() or [""] * 13
    conn.close()
    
    # Safe unpacking Buyer
    b_name = user_data[0] or "Anonymous RPA User"
    b_phone = user_data[1] or "+91 0000000000"
    b_budget = user_data[2] or "50000"
    b_occ = user_data[3] or "Employed"
    b_msg = user_data[5] or "Automatically applied via RPA Bot."
    b_id = (user_data[6] or "").replace("\\", "/")
    b_inc = (user_data[7] or "").replace("\\", "/")
    b_bnk = (user_data[8] or "").replace("\\", "/")

    # Safe unpacking Seller Static Info
    s_owner = user_data[9] or "Seller"
    s_phone = user_data[10] or "+91 9999999999"
    s_email = user_data[11] or ""
    s_id = (user_data[12] or "").replace("\\", "/")

    # Extract dynamic property details from req
    s_title = req.get("p_title", "")
    s_price = req.get("p_price", "")
    s_cat = req.get("p_cat", "")
    s_loc = req.get("p_loc", "")
    s_desc = req.get("p_desc", "")
    s_beds = req.get("p_beds", "")
    s_baths = req.get("p_baths", "")
    s_area = req.get("p_area", "")
    s_type = req.get("p_type", "")
    s_floor = req.get("p_floor", "")
    s_tfloors = req.get("p_tfloors", "")
    s_furn = req.get("p_furn", "")
    s_facing = req.get("p_facing", "")
    s_img = req.get("p_img", "")
    s_own = req.get("p_own", "")
    s_am = req.get("p_am", "")
    s_map = req.get("p_map", "")
    csv_file = req.get("csv_file", "")
    apply_cat = req.get("apply_cat", "All")
    apply_loc = req.get("apply_loc", "")
    apply_type = req.get("apply_type", "")
    apply_budget = req.get("apply_budget", "") or req.get("param1", "")

    robot_cmd = "robot"
    venv_robot = os.path.join(os.path.dirname(os.path.dirname(__file__)), "venv", "Scripts", "robot.exe")
    if os.path.exists(venv_robot):
        robot_cmd = venv_robot

    task_param = req.get("param1", "")
    if not task_param and req.get("task") == "auto_approve":
        task_param = "75"

    try:
        current_process = subprocess.Popen(
            [
                robot_cmd, 
                "-v", f"DELAY:{req['speed']}", 
                "-v", f"USER_EMAIL:{req['email']}", 
                "-v", f"USER_PASS:{req['password']}",
                "-v", f"TASK_PARAM:{task_param}",
                "-v", f"APPLY_CAT:{apply_cat}",
                "-v", f"APPLY_LOC:{apply_loc}",
                "-v", f"APPLY_TYPE:{apply_type}",
                "-v", f"APPLY_BUDGET:{apply_budget}",
                "-v", f"BUYER_NAME:{b_name}",
                "-v", f"BUYER_PHONE:{b_phone}",
                "-v", f"BUYER_BUDGET:{b_budget}",
                "-v", f"BUYER_OCCUPATION:{b_occ}",
                "-v", f"BUYER_MSG:{b_msg}",
                "-v", f"BUYER_ID_DOC:{b_id}",
                "-v", f"BUYER_INCOME_DOC:{b_inc}",
                "-v", f"BUYER_BANK_DOC:{b_bnk}",
                "-v", f"S_TITLE:{s_title}",
                "-v", f"S_PRICE:{s_price}",
                "-v", f"S_CAT:{s_cat}",
                "-v", f"S_LOC:{s_loc}",
                "-v", f"S_DESC:{s_desc}",
                "-v", f"S_BEDS:{s_beds}",
                "-v", f"S_BATHS:{s_baths}",
                "-v", f"S_AREA:{s_area}",
                "-v", f"S_TYPE:{s_type}",
                "-v", f"S_OWNER:{s_owner}",
                "-v", f"S_PHONE:{s_phone}",
                "-v", f"S_EMAIL:{s_email}",
                "-v", f"S_AM:{s_am}",
                "-v", f"S_MAP:{s_map}",
                "-v", f"S_FLOOR:{s_floor}",
                "-v", f"S_TFLOORS:{s_tfloors}",
                "-v", f"S_FURN:{s_furn}",
                "-v", f"S_FACING:{s_facing}",
                "-v", f"S_IMG:{s_img}",
                "-v", f"S_ID:{s_id}",
                "-v", f"S_OWN:{s_own}",
                "-v", f"CSV_FILE:{csv_file}",
                script_path
            ],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Read logs in real-time
        for line in current_process.stdout:
            bot_status["logs"] += line
            
        current_process.wait()
        
        if current_process.returncode == 0:
            bot_status["last_run_status"] = "success"
        elif current_process.returncode == -15 or current_process.returncode == 15: # Terminated
            bot_status["logs"] += "\n--- Bot Execution Stopped by User ---\n"
            bot_status["last_run_status"] = "failed"
        else:
            bot_status["last_run_status"] = "failed"
            
    except Exception as e:
        bot_status["logs"] += f"\nError executing bot: {str(e)}"
        bot_status["last_run_status"] = "failed"
    finally:
        bot_status["is_running"] = False
        current_process = None

@app.get("/api/status")
def get_status():
    return bot_status

@app.post("/api/signup")
def signup(req: AuthRequest):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (req.email, req.password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"user_id": user_id, "email": req.email, "message": "Signup successful"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.post("/api/login")
def login(req: AuthRequest):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (req.email, req.password))
    user = cursor.fetchone()
    if user:
        col_names = [description[0] for description in cursor.description]
        user_dict = dict(zip(col_names, user))
        user_dict["user_id"] = user_dict["id"]
        user_dict["message"] = "Login successful"
        conn.close()
        return user_dict
    conn.close()
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/settings")
def save_settings(
    user_id: int = Form(...),
    plotify_email: str = Form(""),
    plotify_password: str = Form(""),
    seller_plotify_email: str = Form(""),
    seller_plotify_password: str = Form(""),
    buyer_name: str = Form(""),
    buyer_phone: str = Form(""),
    buyer_budget: str = Form(""),
    buyer_occupation: str = Form(""),
    buyer_moving_date: str = Form(""),
    buyer_message: str = Form(""),
    existing_identity: str = Form(""),
    existing_income: str = Form(""),
    existing_bank: str = Form(""),
    identity_doc: UploadFile = File(None),
    income_doc: UploadFile = File(None),
    bank_doc: UploadFile = File(None),
    seller_title: str = Form(""),
    seller_price: str = Form(""),
    seller_category: str = Form(""),
    seller_location: str = Form(""),
    seller_description: str = Form(""),
    seller_bedrooms: str = Form(""),
    seller_bathrooms: str = Form(""),
    seller_area: str = Form(""),
    seller_type: str = Form(""),
    seller_owner_name: str = Form(""),
    seller_phone: str = Form(""),
    seller_email: str = Form(""),
    seller_amenities: str = Form(""),
    seller_map_link: str = Form(""),
    seller_floor: str = Form(""),
    seller_total_floors: str = Form(""),
    seller_furnishing: str = Form(""),
    seller_facing: str = Form(""),
    existing_s_img: str = Form(""),
    existing_s_id: str = Form(""),
    existing_s_own: str = Form(""),
    seller_image_doc: UploadFile = File(None),
    seller_identity_doc: UploadFile = File(None),
    seller_ownership_doc: UploadFile = File(None)
):
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    def save_file(file: UploadFile, prefix: str):
        if file and file.filename:
            file_path = os.path.join(upload_dir, f"{user_id}_{prefix}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return file_path.replace("\\", "/")
        return None

    new_identity_doc = save_file(identity_doc, "identity") or existing_identity
    new_income_doc = save_file(income_doc, "income") or existing_income
    new_bank_doc = save_file(bank_doc, "bank") or existing_bank
    
    new_s_img = save_file(seller_image_doc, "s_img") or existing_s_img
    new_s_id = save_file(seller_identity_doc, "s_id") or existing_s_id
    new_s_own = save_file(seller_ownership_doc, "s_own") or existing_s_own

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET plotify_email = ?, plotify_password = ?, seller_plotify_email = ?, seller_plotify_password = ?, buyer_name = ?, buyer_phone = ?, buyer_budget = ?, buyer_occupation = ?, buyer_moving_date = ?, buyer_message = ?, buyer_identity_doc = ?, buyer_income_doc = ?, buyer_bank_doc = ?,
            seller_title = ?, seller_price = ?, seller_category = ?, seller_location = ?, seller_description = ?, seller_bedrooms = ?, seller_bathrooms = ?, seller_area = ?, seller_type = ?, seller_owner_name = ?, seller_phone = ?, seller_email = ?, seller_amenities = ?, seller_map_link = ?, seller_floor = ?, seller_total_floors = ?, seller_furnishing = ?, seller_facing = ?, seller_image_doc = ?, seller_identity_doc = ?, seller_ownership_doc = ?
        WHERE id = ?
    """, (plotify_email, plotify_password, seller_plotify_email, seller_plotify_password, buyer_name, buyer_phone, buyer_budget, buyer_occupation, buyer_moving_date, buyer_message, new_identity_doc, new_income_doc, new_bank_doc, seller_title, seller_price, seller_category, seller_location, seller_description, seller_bedrooms, seller_bathrooms, seller_area, seller_type, seller_owner_name, seller_phone, seller_email, seller_amenities, seller_map_link, seller_floor, seller_total_floors, seller_furnishing, seller_facing, new_s_img, new_s_id, new_s_own, user_id))
    conn.commit()
    conn.close()
    
    # Query updated data to return to client
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    updated_user = cursor.fetchone()
    conn.close()
    
    col_names = [description[0] for description in cursor.description]
    user_dict = dict(zip(col_names, updated_user))
    user_dict["user_id"] = user_dict["id"]
    user_dict["message"] = "Settings saved successfully"
    return user_dict

@app.get("/api/users")
def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, plotify_email FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return [
        {"id": u[0], "email": u[1], "plotify_email": u[2] or ""} for u in users
    ]

@app.post("/api/run")
def trigger_bot(
    background_tasks: BackgroundTasks,
    speed: float = Form(0.5),
    task: str = Form("auto_approve"),
    email: str = Form(""),
    password: str = Form(""),
    param1: str = Form(""),
    user_id: int = Form(0),
    apply_cat: str = Form("All"),
    apply_loc: str = Form(""),
    apply_type: str = Form(""),
    apply_budget: str = Form(""),
    p_title: str = Form(""),
    p_price: str = Form(""),
    p_cat: str = Form("Rent"),
    p_type: str = Form("Apartment"),
    p_loc: str = Form(""),
    p_beds: str = Form(""),
    p_baths: str = Form(""),
    p_area: str = Form(""),
    p_floor: str = Form(""),
    p_tfloors: str = Form(""),
    p_desc: str = Form(""),
    p_furn: str = Form("Semi-Furnished"),
    p_facing: str = Form("North"),
    p_am: str = Form(""),
    p_map: str = Form(""),
    p_img: UploadFile = File(None),
    p_own: UploadFile = File(None),
    csv_file: UploadFile = File(None)
):
    if bot_status["is_running"]:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    def save_file(file: UploadFile, prefix: str):
        if file and file.filename:
            file_path = os.path.join(upload_dir, f"run_{prefix}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return file_path.replace("\\", "/")
        return ""

    saved_p_img = save_file(p_img, "p_img")
    saved_p_own = save_file(p_own, "p_own")
    saved_csv = save_file(csv_file, "csv_file")

    run_data = {
        "speed": speed,
        "task": task,
        "email": email,
        "password": password,
        "param1": param1,
        "user_id": user_id,
        "apply_cat": apply_cat,
        "apply_loc": apply_loc,
        "apply_type": apply_type,
        "apply_budget": apply_budget,
        "p_title": p_title,
        "p_price": p_price,
        "p_cat": p_cat,
        "p_type": p_type,
        "p_loc": p_loc,
        "p_beds": p_beds,
        "p_baths": p_baths,
        "p_area": p_area,
        "p_floor": p_floor,
        "p_tfloors": p_tfloors,
        "p_desc": p_desc,
        "p_furn": p_furn,
        "p_facing": p_facing,
        "p_am": p_am,
        "p_map": p_map,
        "p_img": saved_p_img,
        "p_own": saved_p_own,
        "csv_file": saved_csv
    }
    
    background_tasks.add_task(run_robot_bot, run_data)
    return {"message": "Bot triggered successfully"}

@app.post("/api/stop")
def stop_bot():
    global current_process
    if bot_status["is_running"] and current_process:
        current_process.terminate()
        return {"message": "Bot termination signal sent"}
    return {"message": "Bot is not running"}

@app.get("/api/report")
def get_report():
    report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "report.html")
    if os.path.exists(report_path):
        return FileResponse(report_path)
    raise HTTPException(status_code=404, detail="Report not found")

@app.get("/api/log")
def get_log():
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log.html")
    if os.path.exists(log_path):
        return FileResponse(log_path)
    raise HTTPException(status_code=404, detail="Log not found")

@app.get("/api/applications/count")
def get_applications_count(filter: str = "Approved Only"):
    import csv
    # Check generated CSV first
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "approved_applications_report.csv")
    csv_count = 0
    if os.path.exists(csv_path):
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                csv_count = sum(1 for _ in reader)
        except Exception:
            csv_count = 0

    # Query DB as fallback
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plotify-real-estate", "instance", "realestate.db")
    db_count = 0
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if "approved" in filter.lower():
                cursor.execute("SELECT COUNT(*) FROM rental_applications WHERE status = 'Approved'")
            else:
                cursor.execute("SELECT COUNT(*) FROM rental_applications")
            row = cursor.fetchone()
            db_count = row[0] if row else 0
            conn.close()
        except Exception:
            db_count = 0

    return {"count": max(csv_count, db_count)}

@app.get("/api/download/approval-report")
def download_approval_report():
    import csv
    import io
    
    csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "approved_applications_report.csv")
    if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 50:
        return FileResponse(
            csv_file_path,
            media_type="text/csv",
            filename="approved_applications_report.csv"
        )

    # Path to Plotify's database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plotify-real-estate", "instance", "realestate.db")
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp",
        "Applicant Name",
        "Email",
        "Phone",
        "Property Title",
        "Amount",
        "Employment Status",
        "Monthly Income",
        "Status",
        "Score"
    ])
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COALESCE(r.applied_on, datetime('now', 'localtime')) as applied_time,
                    r.applicant_name,
                    r.email,
                    r.phone,
                    COALESCE(p.title, 'N/A') as property_title,
                    COALESCE(p.price, 'N/A') as property_price,
                    r.employment_status,
                    r.monthly_income,
                    r.status,
                    COALESCE(r.ai_suitability_score, 'N/A') as ai_score
                FROM rental_applications r
                LEFT JOIN properties p ON r.property_id = p.id
                ORDER BY r.rowid ASC
            """)
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                writer.writerow(row)
        except Exception:
            pass
            
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=approved_applications_report.csv"}
    )

@app.get("/api/buyer/approved-count")
def get_buyer_approved_count(email: str = ""):
    import csv
    # Check generated CSV first
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "buyer_approved_properties.csv")
    csv_count = 0
    if os.path.exists(csv_path):
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                csv_count = sum(1 for _ in reader)
        except Exception:
            csv_count = 0

    # Query DB as fallback
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plotify-real-estate", "instance", "realestate.db")
    db_count = 0
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if email:
                cursor.execute("SELECT COUNT(*) FROM rental_applications WHERE (email = ? OR applicant_name = ?) AND status = 'Approved'", (email, email))
            else:
                cursor.execute("SELECT COUNT(*) FROM rental_applications WHERE status = 'Approved'")
            row = cursor.fetchone()
            db_count = row[0] if row else 0
            conn.close()
        except Exception:
            db_count = 0

    return {"count": max(csv_count, db_count)}

@app.get("/api/buyer/download-approved")
def download_buyer_approved(email: str = ""):
    import csv
    import io
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "buyer_approved_properties.csv")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 50:
        return FileResponse(
            csv_path,
            media_type="text/csv",
            filename="buyer_approved_properties.csv"
        )
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plotify-real-estate", "instance", "realestate.db")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Applied On",
        "Property Title",
        "Location",
        "Amount",
        "Owner Name",
        "Owner Phone",
        "Owner Email",
        "Status",
        "Score"
    ])
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            query = """
                SELECT 
                    COALESCE(r.applied_on, datetime('now', 'localtime')),
                    COALESCE(p.title, 'N/A'),
                    COALESCE(p.location, 'N/A'),
                    COALESCE(p.price, 'N/A'),
                    COALESCE(p.owner_name, 'Seller'),
                    COALESCE(p.phone, 'N/A'),
                    COALESCE(p.email, 'N/A'),
                    r.status,
                    COALESCE(r.ai_suitability_score, 'N/A')
                FROM rental_applications r
                JOIN properties p ON r.property_id = p.id
                WHERE r.status = 'Approved'
            """
            params = []
            if email:
                query += " AND (r.email = ? OR r.applicant_name = ?)"
                params = [email, email]
            query += " ORDER BY r.rowid DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                writer.writerow(row)
        except Exception:
            pass

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=buyer_approved_properties.csv"}
    )

