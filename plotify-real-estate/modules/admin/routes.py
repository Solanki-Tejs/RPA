from flask import render_template, redirect, request, session
from modules.models import Property, PendingProperty, User, Agent
from modules.admin import admin_bp
from functools import wraps

# ===============================
# ADMIN PROTECTION DECORATOR
# ===============================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin-login")
        return f(*args, **kwargs)
    return decorated_function


# ===============================
# ADMIN LOGIN
# ===============================
@admin_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")
        else:
            return render_template("admin/login.html", error="Invalid credentials")

    return render_template("admin/login.html")


# ===============================
# ADMIN DASHBOARD
# ===============================
@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    total = Property.query.count()
    pending_count = PendingProperty.query.count()
    sold = Property.query.filter_by(status="Sold").count()
    rented = Property.query.filter_by(status="Rented").count()

    pending = PendingProperty.query.all()

    return render_template("admin/dashboard.html",
                           total=total,
                           pending_count=pending_count,
                           sold=sold,
                           rented=rented,
                           pending=pending
                           )


# ===============================
# APPROVE PROPERTY
# ===============================
@admin_bp.route("/admin/approve/<id>")
@admin_required
def approve_property(id):
    p = PendingProperty.query.get(id)

    new_property = Property(
    title=p.title,
    price=p.price,
    category=p.category,
    location=p.location,
    description=p.description,
    bedrooms=p.bedrooms,
    bathrooms=p.bathrooms,
    area=p.area,
    type=p.type,
    status=p.status,
    owner_name=p.owner_name,
    phone=p.phone,
    email=p.email,
    image=p.image,
    posted=p.posted,
    amenities=p.amenities,
    identity_doc=p.identity_doc,
    ownership_doc=p.ownership_doc,
    map_link=p.map_link,
    floor=p.floor,
    total_floors=p.total_floors,
    furnishing=p.furnishing,
    facing=p.facing,
    user_id=p.user_id,
    featured=True
)


    from modules.models import db
    db.session.add(new_property)
    db.session.delete(p)
    db.session.commit()

    return redirect("/admin")


# ===============================
# DELETE PENDING
# ===============================
@admin_bp.route("/admin/delete-pending/<id>")
@admin_required
def delete_pending(id):
    from modules.models import db
    p = PendingProperty.query.get(id)
    db.session.delete(p)
    db.session.commit()
    return redirect("/admin")


# ===============================
# VIEW ALL PROPERTIES
# ===============================
@admin_bp.route("/admin/properties")
@admin_required
def admin_properties():
    properties = Property.query.all()
    return render_template("admin/manage_properties.html", properties=properties)


# ===============================
# CHANGE STATUS
# ===============================
@admin_bp.route("/admin/status/<id>/<status>")
@admin_required
def change_status(id, status):
    from modules.models import db
    p = Property.query.get(id)
    p.status = status
    db.session.commit()
    return redirect("/admin/properties")


# ===============================
# EDIT PROPERTY
# ===============================
@admin_bp.route("/admin/edit/<id>", methods=["GET", "POST"])
@admin_required
def edit_property(id):
    from modules.models import db
    p = Property.query.get(id)

    if request.method == "POST":
        p.price = request.form["price"]
        p.location = request.form["location"]
        p.bedrooms = request.form["bedrooms"]
        p.bathrooms = request.form["bathrooms"]
        db.session.commit()
        return redirect("/admin/properties")

    return render_template("admin/edit_property.html", property=p)


# ===============================
# USERS
# ===============================
@admin_bp.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin/manage_users.html", users=users)


# ===============================
# AGENTS
# ===============================
@admin_bp.route("/admin/agents")
@admin_required
def admin_agents():
    agents = Agent.query.all()
    return render_template("admin/manage_agents.html", agents=agents)


# ===============================
# ADD AGENT
# ===============================
@admin_bp.route("/admin/add-agent", methods=["POST"])
@admin_required
def add_agent():
    from modules.models import db

    new = Agent(
        name=request.form["name"],
        specialization=request.form["specialization"],
        city=request.form["city"],
        experience=request.form["experience"],
        phone=request.form["phone"]
    )

    db.session.add(new)
    db.session.commit()

    return redirect("/admin/agents")


# ===============================
# DELETE AGENT
# ===============================
@admin_bp.route("/admin/delete-agent/<id>")
@admin_required
def delete_agent(id):
    from modules.models import db
    a = Agent.query.get(id)
    db.session.delete(a)
    db.session.commit()
    return redirect("/admin/agents")



# BLOCK USER
@admin_bp.route("/admin/block/<id>")
def block_user(id):
    from modules.models import db
    u = User.query.get(id)
    u.is_blocked = not u.is_blocked
    db.session.commit()
    return redirect("/admin/users")


# DELETE USER
@admin_bp.route("/admin/delete-user/<id>")
def delete_user(id):
    from modules.models import db
    u = User.query.get(id)
    db.session.delete(u)
    db.session.commit()
    return redirect("/admin/users")



# ===============================
# LOGOUT
# ===============================
@admin_bp.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin-login")


# ===============================
# RENTAL APPLICATIONS
# ===============================
@admin_bp.route("/admin/applications")
@admin_required
def admin_applications():
    from modules.models import RentalApplication
    apps = RentalApplication.query.all()
    return render_template("admin/manage_applications.html", applications=apps)

@admin_bp.route("/admin/application/update/<id>", methods=["POST"])
@admin_required
def update_application(id):
    from modules.models import db, RentalApplication
    app_entry = RentalApplication.query.get(id)
    if app_entry:
        if request.form.get("status"):
            app_entry.status = request.form.get("status")
        if request.form.get("ai_suitability_score"):
            app_entry.ai_suitability_score = request.form.get("ai_suitability_score")
        if request.form.get("admin_notes"):
            app_entry.admin_notes = request.form.get("admin_notes")
        db.session.commit()
    return redirect("/admin/applications")
