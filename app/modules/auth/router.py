from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response, error_response
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.core.dependencies import get_current_user
from app.modules.auth import schemas, models
from app.modules.transporter.profile.models import TransporterProfile
from app.modules.transporter.vehicles.models import Vehicle
from datetime import datetime, timezone, timedelta
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=StandardResponse[schemas.LoginResponse])
def register(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(models.User).filter(models.User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.mobile == request.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile already registered")
    if db.query(Vehicle).filter(Vehicle.vehicle_number == request.vehicleNumber).first():
        raise HTTPException(status_code=409, detail="Vehicle number already registered")
        
    # Create User
    new_user = models.User(
        name=request.name,
        email=request.email,
        mobile=request.mobile,
        password_hash=get_password_hash(request.password),
        role="TRANSPORTER",
        status="ACTIVE"
    )
    db.add(new_user)
    try:
        db.flush() # Obtain ID without committing a partially registered account.
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or mobile already registered")
    
    # Create Profile
    new_profile = TransporterProfile(
        user_id=new_user.id,
        company_name=request.name, # Use name as company for now
        contact_person=request.name,
        city=request.city,
        state=request.state
    )
    db.add(new_profile)
    
    # Parse Capacity safely
    capacity_val = 0.0
    import re
    match = re.search(r'\d+', request.capacity)
    if match:
        capacity_val = float(match.group())

    # Create Vehicle
    new_vehicle = Vehicle(
        transporter_id=new_user.id,
        vehicle_type=request.vehicleType,
        vehicle_number=request.vehicleNumber,
        capacity=capacity_val,
        capacity_unit="Tons"
    )
    db.add(new_vehicle)
    
    # Generate Tokens
    access_token = create_access_token(subject=new_user.id, role=new_user.role)
    refresh_token = create_refresh_token(subject=new_user.id, role=new_user.role)
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = models.RefreshToken(
        user_id=new_user.id,
        token=refresh_token,
        expires_at=expires_at
    )
    db.add(db_token)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email, mobile or vehicle number already registered")
    db.refresh(new_user)
    
    return success_response(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": new_user
    }, message="Registration successful")

@router.post("/login", response_model=StandardResponse[schemas.LoginResponse])
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if user.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    if user.role != "TRANSPORTER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A transporter account is required")

    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id, role=user.role)
    
    # Store refresh token in db
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()

    return success_response(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }, message="Login successful")

@router.post("/refresh", response_model=StandardResponse[schemas.TokenResponse])
def refresh(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(request.refresh_token, "refresh")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == request.refresh_token,
        models.RefreshToken.is_revoked == False
    ).with_for_update().first()
    
    if not db_token or db_token.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user = db.query(models.User).filter(models.User.id == payload.get("sub")).first()
    if not user or user.status != "ACTIVE" or user.role != "TRANSPORTER":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is not available")
    
    # Optional: revoke old refresh token (token rotation)
    db_token.is_revoked = True
    
    user_id = user.id
    role = user.role
    access_token = create_access_token(subject=user_id, role=role)
    new_refresh_token = create_refresh_token(subject=user_id, role=role)
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = models.RefreshToken(
        user_id=user_id,
        token=new_refresh_token,
        expires_at=expires_at
    )
    db.add(new_db_token)
    db.commit()
    
    return success_response(data={
        "access_token": access_token,
        "refresh_token": new_refresh_token
    })

@router.post("/logout", response_model=StandardResponse)
def logout(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == request.refresh_token
    ).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
    return success_response(message="Logged out successfully")

@router.get("/me", response_model=StandardResponse[schemas.UserResponse])
def get_me(current_user: models.User = Depends(get_current_user)):
    return success_response(data=current_user)
