from app import app
from modules.models import db, User, Property, RentalApplication

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating tables...")
    db.create_all()

    print("Seeding users...")
    seller = User(name="Seller User", email="user@gamil.com", password="user123", role="seller")
    buyer = User(name="Test Tenant", email="testuser2@example.com", password="TestPassword123", role="buyer")
    db.session.add(seller)
    db.session.add(buyer)
    db.session.commit()

    print("Seeding a rental property...")
    prop = Property(
        title="Modern Apartment in City Center",
        price="15000",
        category="Rent",
        location="Downtown",
        description="A beautiful and modern apartment perfect for city living.",
        bedrooms="2",
        bathrooms="2",
        area="1200 sqft",
        type="Apartment",
        owner_name="Seller User",
        phone="+91 99999 00000",
        email="user@gamil.com",
        image="house2.png",
        user_id=seller.id
    )
    db.session.add(prop)
    db.session.commit()

    print("Database reset and seeded successfully!")
