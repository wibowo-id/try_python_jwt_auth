from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, database, utils, config
from datetime import timedelta
from jose import JWTError, jwt

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = utils.hash_password(user.password)
    verification_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=60)
    )
    
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        is_verified=False,
        verification_token=verification_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    utils.send_verification_email(user.email, verification_token)
    return {"msg": "Registered successfully. Check your email to verify account."}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = utils.create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = utils.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=config.RESET_PASSWORD_EXPIRE_MINUTES)
    )
    user.reset_token = token
    db.commit()
    utils.send_reset_email(user.email, token)
    return {"msg": "Reset token sent to email"}

@router.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(models.User).filter(models.User.email == email, models.User.reset_token == request.token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or invalid token")

    user.hashed_password = utils.hash_password(request.new_password)
    user.reset_token = None
    db.commit()
    return {"msg": "Password reset successful"}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(models.User).filter(models.User.email == email, models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"msg": "Email verified successfully"}