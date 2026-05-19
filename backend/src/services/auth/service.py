from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status

from src.utils.db import db
from src.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    async def register_user(self, email: str, password: str, full_name: str) -> dict:
        existing = await db.db.users.find_one({"email": email.lower()})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        now = datetime.now(timezone.utc)
        document = {
            "email": email.lower(),
            "full_name": full_name.strip(),
            "password_hash": hash_password(password),
            "created_at": now,
            "updated_at": now,
        }
        result = await db.db.users.insert_one(document)
        user_id = str(result.inserted_id)
        return {
            "id": user_id,
            "email": document["email"],
            "full_name": document["full_name"],
            "access_token": create_access_token(user_id, {"email": document["email"]}),
        }

    async def login_user(self, email: str, password: str) -> dict:
        user = await db.db.users.find_one({"email": email.lower()})
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        user_id = str(user["_id"])
        return {
            "id": user_id,
            "email": user["email"],
            "full_name": user["full_name"],
            "access_token": create_access_token(user_id, {"email": user["email"]}),
        }

    async def get_user_by_id(self, user_id: str) -> dict:
        try:
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

        user = await db.db.users.find_one({"_id": object_id})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
        }


auth_service = AuthService()
