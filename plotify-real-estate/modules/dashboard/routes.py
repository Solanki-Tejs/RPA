import csv
import io
from flask import Blueprint, render_template, session, redirect, url_for, request, Response
from modules.models import db, Property, RentalApplication, User

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    template_folder="../../templates",
    url_prefix="/dashboard"
)

# =========================
# SELLER DASHBOARD
# =========================
@dashboard_bp.route("/seller")
def seller_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    
    user_id = session.get("user_id")
    # Get all properties owned by this seller
    seller_properties = Property.query.filter_by(user_id=user_id).all()
    
    # Get all applications for this seller's properties
    applications = RentalApplication.query.join(Property).filter(Property.user_id == user_id).all()
    
    active_tab = request.args.get("tab", "new")
    
    return render_template(
        "dashboard/seller.html",
        properties=seller_properties,
        applications=applications,
        active_tab=active_tab
    )

# =========================
# BUYER DASHBOARD
# =========================
@dashboard_bp.route("/buyer")
def buyer_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
        
    user_id = session.get("user_id")
    # Get all applications made by this buyer
    applications = RentalApplication.query.filter_by(user_id=user_id).all()
    
    return render_template(
        "dashboard/buyer.html",
        applications=applications
    )

# =========================
# UPDATE APPLICATION STATUS (FOR SELLER / RPA)
# =========================
@dashboard_bp.route("/update_application/<app_id>", methods=["POST"])
def update_application(app_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
        
    application = RentalApplication.query.get(app_id)
    if not application:
        return "Application not found", 404
        
    # Verify the logged in user is the owner of the property
    if application.property.user_id != session.get("user_id"):
        return "Unauthorized", 403
        
    new_status = request.form.get("status")
    ai_score = request.form.get("ai_suitability_score")
    
    if new_status:
        application.status = new_status
    if ai_score is not None:
        application.ai_suitability_score = ai_score
        
    db.session.commit()
    return redirect(url_for("dashboard.seller_dashboard"))


# =========================
# BUYER EXPORT APPROVED TO CSV
# =========================
@dashboard_bp.route("/buyer/export_csv")
def buyer_export_csv():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
        
    user_id = session.get("user_id")
    approved_apps = RentalApplication.query.filter_by(user_id=user_id, status="Approved").all()
    
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
    
    for app in approved_apps:
        prop = app.property
        score_val = (app.ai_suitability_score or "N/A").replace("Rent is", "Amount is")
        writer.writerow([
            app.applied_on or "N/A",
            prop.title if prop else "N/A",
            prop.location if prop else "N/A",
            prop.price if prop else "N/A",
            prop.owner_name if prop and prop.owner_name else "Seller",
            prop.phone if prop and prop.phone else "N/A",
            prop.email if prop and prop.email else "N/A",
            app.status,
            score_val
        ])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=buyer_approved_properties.csv"}
    )

