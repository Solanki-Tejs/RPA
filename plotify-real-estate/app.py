import os
from flask import Flask, render_template
from modules.models import db, Property
from modules.auth.routes import auth_bp

from modules.buy import buy_bp
from modules.rent import rent_bp
from modules.sell import sell_bp
from modules.agents import agents_bp
from modules.commercial import commercial_bp
from modules.admin import admin_bp
from modules.dashboard.routes import dashboard_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///realestate.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# UPLOAD
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# REGISTER BLUEPRINTS
app.register_blueprint(buy_bp)
app.register_blueprint(rent_bp)
app.register_blueprint(sell_bp)
app.register_blueprint(agents_bp)
app.register_blueprint(commercial_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# HOME
@app.route("/")
def home():
    featured_properties = Property.query.limit(6).all()
    return render_template("buyer/home.html", properties=featured_properties)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
