from fastapi import FastAPI
from . import models, database
from .auth import router as auth_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Auth API")

app.include_router(auth_router)
