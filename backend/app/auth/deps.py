from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

security = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    return {
        "id": "dev-user",
        "role": "admin",
        "email": "dev-admin@example.com",
    }


def require_admin():
    return {"id": "dev-user", "role": "admin", "email": "dev-admin@example.com"}