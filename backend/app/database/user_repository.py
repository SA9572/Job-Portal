from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database.user_model import UserModel
from app.core.security import hash_password


class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        statement = select(UserModel).where(UserModel.id == user_id)
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        if not email:
            return None
        clean_email = email.strip().lower()
        statement = select(UserModel).where(UserModel.email == clean_email)
        return self.session.execute(statement).scalar_one_or_none()

    def create(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "user",
    ) -> UserModel:
        clean_email = email.strip().lower()
        hashed_pwd = hash_password(password)
        now = datetime.now(timezone.utc)

        clean_role = role.strip().lower() if role else "user"

        user = UserModel(
            email=clean_email,
            hashed_password=hashed_pwd,
            full_name=full_name.strip() if full_name else None,
            role=clean_role,
            is_superuser=(clean_role == "admin"),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_users(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[UserModel], int]:
        statement = select(UserModel).order_by(UserModel.id.desc())

        count_stmt = select(func.count(UserModel.id))
        total = self.session.execute(count_stmt).scalar_one()

        users = list(
            self.session.execute(
                statement.offset(offset).limit(limit)
            ).scalars().all()
        )

        return users, total
