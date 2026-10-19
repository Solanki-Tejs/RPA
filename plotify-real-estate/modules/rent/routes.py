import os
import uuid
import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from modules.models import db, Property, RentalApplication

rent_bp = Blueprint(
    "rent",
    __name__,
    template_folder="../../templates"
)

# =========================
# RENT PAGE
# =========================
@rent_bp.route("/rent")
def rent():

    properties = Property.query.filter_by(
        category="Rent",
        verified=True
    ).all()

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
        "rent.html",
        properties=properties,
        applied_ids=applied_ids
    )

# =========================
# RENT PROPERTY DETAILS
# =========================
@rent_bp.route("/rent/<id>")
def rent_details(id):

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

# =========================
# APPLY FOR RENT
# =========================
@rent_bp.route("/apply_rent/<id>", methods=["GET", "POST"])
def apply_rent(id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    prop = Property.query.get(id)
    if not prop:
        return "Property not found"

    def get_details_url(p):
        cat = (p.category or "").strip().lower()
        if cat == "commercial":
            return url_for("commercial.commercial_details", id=p.id)
        elif cat == "buy":
            return url_for("buy.property_details", id=p.id)
        return url_for("rent.rent_details", id=p.id)

    # Cannot apply to your own property
    if prop.user_id and prop.user_id == session.get("user_id"):
        return redirect(get_details_url(prop))

    # Check if user has already applied
    user_id = session.get("user_id")
    user_email = session.get("user_email")
    filter_cond = []
    if user_id:
        filter_cond.append(RentalApplication.user_id == user_id)
    if user_email:
        filter_cond.append(RentalApplication.email == user_email)

    existing_app = RentalApplication.query.filter(
        RentalApplication.property_id == id,
        db.or_(*filter_cond)
    ).first()

    # Block access if already applied once
    if existing_app:
        return redirect(get_details_url(prop))

    if request.method == "POST":
        form_email = request.form.get("email")
        if form_email:
            existing_by_email = RentalApplication.query.filter_by(property_id=id, email=form_email).first()
            if existing_by_email:
                return redirect(get_details_url(prop))

        # Handle Documents
        id_doc = request.files.get("identity_doc")
        income_doc = request.files.get("income_proof_doc")
        bank_doc = request.files.get("bank_statement_doc")

        id_name = ""
        income_name = ""
        bank_name = ""

        if id_doc and id_doc.filename:
            id_name = secure_filename(id_doc.filename)
            id_doc.save(os.path.join("static/uploads", id_name))
        
        if income_doc and income_doc.filename:
            income_name = secure_filename(income_doc.filename)
            income_doc.save(os.path.join("static/uploads", income_name))
            
        if bank_doc and bank_doc.filename:
            bank_name = secure_filename(bank_doc.filename)
            bank_doc.save(os.path.join("static/uploads", bank_name))

        new_app = RentalApplication(
            id=str(uuid.uuid4()),
            property_id=id,
            user_id=session.get("user_id"),
            applicant_name=request.form.get("applicant_name"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            employment_status=request.form.get("employment_status"),
            monthly_income=request.form.get("monthly_income"),
            message=request.form.get("message"),
            identity_doc=id_name,
            income_proof_doc=income_name,
            bank_statement_doc=bank_name,
            applied_on=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        db.session.add(new_app)
        db.session.commit()

        return redirect(get_details_url(prop))

    return render_template("buyer/apply_rent.html", property=prop)
