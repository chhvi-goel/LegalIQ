from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User, AuditLog
from app.models.auth import UserCreate, UserLogin, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        # Default guest user for seamless demo usage if no token sent
        guest = db.query(User).filter(User.email == "demo@legaliq.ai").first()
        if not guest:
            guest = User(
                email="demo@legaliq.ai",
                hashed_password=get_password_hash("demo1234"),
                full_name="LegalIQ Demo User",
                role="lawyer"
            )
            db.add(guest)
            db.commit()
            db.refresh(guest)
        return guest
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

@router.post("/register", response_model=Token)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role or "citizen",
        organization=user_in.organization
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Audit log
    audit = AuditLog(user_id=user.id, action="USER_REGISTER", details={"email": user.email, "role": user.role})
    db.add(audit)
    db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    return Token(access_token=token, token_type="bearer", user=UserResponse.from_orm(user))

@router.post("/login", response_model=Token)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Audit log
    audit = AuditLog(user_id=user.id, action="USER_LOGIN", details={"email": user.email})
    db.add(audit)
    db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    return Token(access_token=token, token_type="bearer", user=UserResponse.from_orm(user))

@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
