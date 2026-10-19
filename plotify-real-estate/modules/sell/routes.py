import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from modules.models import db, Property

sell_bp = Blueprint(
    "sell",
    __name__,
    template_folder="../../templates"
)

@sell_bp.route("/sell", methods=["GET", "POST"])
def sell_property():

    # 🔒 LOGIN REQUIRED
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        # ---------- IMAGE ----------
        image_file = request.files.get("images")
        image_name = "default.jpg"

        if image_file and image_file.filename:
            image_name = secure_filename(image_file.filename)
            image_file.save(os.path.join("static/uploads", image_name))

        # ---------- DOCUMENTS ----------
        identity_file = request.files.get("identity_doc")
        ownership_file = request.files.get("ownership_doc")

        identity_name = ""
        ownership_name = ""

        if identity_file and identity_file.filename:
            identity_name = secure_filename(identity_file.filename)
            identity_file.save(os.path.join("static/uploads", identity_name))

        if ownership_file and ownership_file.filename:
            ownership_name = secure_filename(ownership_file.filename)
            ownership_file.save(os.path.join("static/uploads", ownership_name))

        # ---------- AMENITIES ----------
        amenities_list = request.form.getlist("amenities")
        amenities_str = ", ".join(amenities_list)

        # ⭐ IMPORTANT — GET LOGGED USER ID
        current_user_id = session.get("user_id")

        # ---------- SAVE PROPERTY ----------
        new_property = Property(
            id=str(uuid.uuid4()),
            title=request.form.get("title"),
            price=request.form.get("price"),
            category=request.form.get("category"),
            location=request.form.get("location"),
            description=request.form.get("description"),
            bedrooms=request.form.get("bedrooms"),
            bathrooms=request.form.get("bathrooms"),
            area=request.form.get("area"),
            type=request.form.get("type"),
            status="Ready to Move",

            owner_name=request.form.get("owner_name"),
            phone=request.form.get("phone"),
            email=request.form.get("email"),

            image=image_name,
            posted="today",

            amenities=amenities_str,
            identity_doc=identity_name,
            ownership_doc=ownership_name,
            map_link=request.form.get("map_link"),
            floor=request.form.get("floor"),
            total_floors=request.form.get("total_floors"),
            furnishing=request.form.get("furnishing"),
            facing=request.form.get("facing"),

            # ⭐ THIS FIXES YOUR ERROR
            user_id=current_user_id
        )

        db.session.add(new_property)
        db.session.commit()

        return redirect(url_for("sell.sell_property"))

    return render_template("seller/sell.html")
