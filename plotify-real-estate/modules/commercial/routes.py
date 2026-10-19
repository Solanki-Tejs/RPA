from flask import Blueprint, render_template, abort, session
from modules.models import db, Property, RentalApplication

commercial_bp = Blueprint(
    "commercial",
    __name__,
    template_folder="../../templates"
)

# -----------------------------
# COMMERCIAL LIST PAGE
# -----------------------------
@commercial_bp.route("/commercial")
def commercial():
    properties = Property.query.filter_by(category="Commercial").all()

    applied_ids = []
    user_id = session.get("user_id")
    user_email = session.get("user_email")
    if user_id or user_email:
        filter_cond = []
        if user_id:
            filter_cond.append(RentalApplication.user_id == user_id)
        if user_email:
            filter_cond.append(RentalApplication.email == user_email)
        applied_apps = RentalApplication.query.filter(db.or_(*filter_cond)).all()
        applied_ids = [app.property_id for app in applied_apps]

    return render_template("commercial.html", properties=properties, applied_ids=applied_ids)


# -----------------------------
# COMMERCIAL PROPERTY DETAILS
# -----------------------------
@commercial_bp.route("/commercial/<id>")
def commercial_details(id):
    property_data = Property.query.get_or_404(id)

    existing_app = None
    user_id = session.get("user_id")
    user_email = session.get("user_email")
    if user_id or user_email:
        filter_cond = []
        if user_id:
            filter_cond.append(RentalApplication.user_id == user_id)
        if user_email:
            filter_cond.append(RentalApplication.email == user_email)
        existing_app = RentalApplication.query.filter(
            RentalApplication.property_id == id,
            db.or_(*filter_cond)
        ).first()

    return render_template(
        "buyer/property_details.html",
        property=property_data,
        existing_app=existing_app
    )
