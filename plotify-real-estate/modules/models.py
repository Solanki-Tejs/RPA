from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

# ==============================
# USERS TABLE
# ==============================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200))

    last_login = db.Column(db.String(50))
    last_seen = db.Column(db.String(50))
    is_blocked = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default="buyer")  # 'buyer' or 'seller'

    # RELATIONSHIPS
    pending_properties = db.relationship("PendingProperty", backref="user", lazy=True)
    properties = db.relationship("Property", backref="owner", lazy=True)


# ==============================
# MAIN LIVE PROPERTIES (APPROVED)
# ==============================
class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    title = db.Column(db.String(200))
    price = db.Column(db.String(100))
    category = db.Column(db.String(50))   # Sell / Rent / Commercial
    location = db.Column(db.String(200))
    description = db.Column(db.Text)

    bedrooms = db.Column(db.String(10))
    bathrooms = db.Column(db.String(10))
    area = db.Column(db.String(50))
    type = db.Column(db.String(50))        # House / Apartment / Office

    status = db.Column(db.String(50), default="Ready to Move")

    owner_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    image = db.Column(db.String(200))
    posted = db.Column(db.String(50))

    verified = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)

    # EXTRA PROPERTY DETAILS
    amenities = db.Column(db.Text)
    identity_doc = db.Column(db.String(200))
    ownership_doc = db.Column(db.String(200))
    map_link = db.Column(db.String(300))
    floor = db.Column(db.String(20))
    total_floors = db.Column(db.String(20))
    furnishing = db.Column(db.String(50))
    facing = db.Column(db.String(50))

    # LINK TO USER
    user_id = db.Column(db.String, db.ForeignKey("users.id"))


# ==============================
# PENDING PROPERTIES (WAITING ADMIN APPROVAL)
# ==============================
class PendingProperty(db.Model):
    __tablename__ = "pending_properties"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    title = db.Column(db.String(200))
    price = db.Column(db.String(100))
    category = db.Column(db.String(50))
    location = db.Column(db.String(200))
    description = db.Column(db.Text)

    bedrooms = db.Column(db.String(10))
    bathrooms = db.Column(db.String(10))
    area = db.Column(db.String(50))
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))

    owner_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    image = db.Column(db.String(200))
    posted = db.Column(db.String(50))

    # EXTRA DETAILS
    amenities = db.Column(db.Text)
    identity_doc = db.Column(db.String(200))
    ownership_doc = db.Column(db.String(200))
    map_link = db.Column(db.String(300))
    floor = db.Column(db.String(20))
    total_floors = db.Column(db.String(20))
    furnishing = db.Column(db.String(50))
    facing = db.Column(db.String(50))

    # LINK TO USER
    user_id = db.Column(db.String, db.ForeignKey("users.id"))


# ==============================
# AGENTS TABLE
# ==============================
class Agent(db.Model):
    __tablename__ = "agents"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    city = db.Column(db.String(100))
    experience = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    verified = db.Column(db.Boolean, default=True)


# ==============================
# ENQUIRIES TABLE (BUYER CONTACT)
# ==============================
class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    property_id = db.Column(db.String(100))
    property_title = db.Column(db.String(200))
    message = db.Column(db.Text)
    date = db.Column(db.String(50))


# ==============================
# ACTIVITY LOG TABLE (ADMIN TRACKING)
# ==============================
class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action = db.Column(db.String(200))
    admin = db.Column(db.String(100))
    time = db.Column(db.String(50))

# ==============================
# RENTAL APPLICATIONS (FOR RPA BOT)
# ==============================
class RentalApplication(db.Model):
    __tablename__ = "rental_applications"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = db.Column(db.String, db.ForeignKey("properties.id"))
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    
    applicant_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    
    employment_status = db.Column(db.String(50))
    monthly_income = db.Column(db.String(50))
    
    # Document Paths
    identity_doc = db.Column(db.String(200))
    income_proof_doc = db.Column(db.String(200))
    bank_statement_doc = db.Column(db.String(200))
    
    message = db.Column(db.Text)
    
    # Status updated by RPA / Admin
    status = db.Column(db.String(50), default="Pending")
    ai_suitability_score = db.Column(db.String(100))
    admin_notes = db.Column(db.Text)
    
    applied_on = db.Column(db.String(50))

    # Relationships
    property = db.relationship("Property", backref="applications")
    user = db.relationship("User", backref="applications")
