from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate
from app.security import hash_password, verify_password


class UserService:
    @staticmethod
    def get_user_by_email(db: Session, email: str | EmailStr) -> type[User] | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> type[User] | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> type[User] | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        if UserService.get_user_by_email(db, user_create.email):
            raise ValueError("Email already registered")

        if UserService.get_user_by_username(db, user_create.username):
            raise ValueError("Username already taken")

        # Create user
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hash_password(user_create.password),
            role=UserRole.USER,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> type[User] | None:
        user = UserService.get_user_by_username(db, username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> type[User]:
        user = UserService.get_user_by_id(db, user_id)

        if not user:
            raise ValueError("User not found")

        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        if user_update.password is not None:
            user.hashed_password = hash_password(user_update.password)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10):
        total = db.query(User).count()
        users = db.query(User).offset(skip).limit(limit).all()
        return users, total
