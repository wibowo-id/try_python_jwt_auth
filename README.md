# install requirement package
pip install fastapi uvicorn sqlalchemy "passlib[bcrypt]" python-jose email-validator

# config.py
SECRET_KEY = "secretjwtkey"<br>
ALGORITHM = "HS256"<br>
ACCESS_TOKEN_EXPIRE_MINUTES = 30<br>
RESET_PASSWORD_EXPIRE_MINUTES = 15<br>
EMAIL_FROM = "your_gmail@gmail.com"<br>
EMAIL_PASSWORD = "your_app_password"  # Gunakan App Password dari Google<br>
SMTP_SERVER = "smtp.gmail.com"<br>
SMTP_PORT = 587

# running app
uvicorn app.main:app --reload

# if successful running
INFO:     Will watch for changes in these directories: ['/wibowo/try_python_jwt_auth'] <br>
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)<br>
INFO:     Started reloader process [6019] using StatReload<br>
INFO:     Started server process [6021]
