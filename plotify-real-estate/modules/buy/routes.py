from flask import Blueprint, render_template, session
from modules.models import db, Property, RentalApplication

buy_bp = Blueprint(
    "buy",
    __name__,
    template_folder="../../templates"
)

# =========================
# BUY PAGE
# =========================
@buy_bp.route("/buy")
def buy():

    properties = Property.query.filter_by(category="Sell").all()

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

    return render_template(
        "buyer/buy.html",
        properties=properties,
        applied_ids=applied_ids,
        logged_in=bool(user_id)
    )

# =========================
# PROPERTY DETAILS PAGE
# =========================
@buy_bp.route("/property/<id>")
def property_details(id):

    prop = Property.query.get(id)

    if not prop:
        return "Property not found"

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
        property=prop,
        existing_app=existing_app
    )
