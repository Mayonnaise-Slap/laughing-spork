from app.database import engine, SessionLocal
from app.models import Base, User, UserRole
from app.security import hash_password


# todo read from config
def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created")

    db = SessionLocal()

    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            full_name="Administrator",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        print("Created default admin user")
        print("Email: admin@example.com")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin user already exists")

    db.close()
    print("Database initialization complete")


if __name__ == "__main__":
    init_db()
