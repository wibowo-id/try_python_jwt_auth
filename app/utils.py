import smtplib
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from email.message import EmailMessage
from . import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_FROM
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)
        smtp.send_message(msg)

def send_verification_email(email: str, token: str):
    verify_link = f"http://localhost:8000/verify-email?token={token}"
    body = f"Klik link ini untuk verifikasi akun kamu: {verify_link}"
    send_email(email, "Verifikasi Email", body)

def send_reset_email(email: str, token: str):
    reset_link = f"http://localhost:8000/reset-password-page?token={token}"
    body = f"Klik link ini untuk reset password: {reset_link}"
    send_email(email, "Reset Password", body)
