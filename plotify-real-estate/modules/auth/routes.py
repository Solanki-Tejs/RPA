from flask import Blueprint, render_template, request, redirect, url_for, session
from modules.models import db, User
import uuid
from datetime import datetime

auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="../../templates"
)

# ================= SIGNUP =================
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        role = request.form.get("role", "buyer")

        # confirm password check
        if password != confirm:
            return render_template("auth/signup.html", error="Passwords do not match")

        # email already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template("auth/signup.html", error="Email already registered")

        new_user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


# ================= LOGIN =================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            session["user_email"] = user.email

            # SAVE LOGIN TIME
            user.last_login = str(datetime.now())
            db.session.commit()

            return redirect(url_for("home"))

        return render_template("auth/login.html", error="Invalid credentials")

    return render_template("auth/login.html")

# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
