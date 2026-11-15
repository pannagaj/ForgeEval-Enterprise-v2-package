from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import token_subject
from app.models import User

bearer = HTTPBearer(auto_error=False)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(401, "Authentication required")
    subject = token_subject(credentials.credentials)
    user = db.get(User, int(subject)) if subject and subject.isdigit() else None
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user

def admin_user(user: User = Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required")
    return user
