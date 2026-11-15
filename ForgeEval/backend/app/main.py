from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base, engine
from app.api import router
from app.seed import seed

app = FastAPI(title=settings.app_name, version="1.0.0", description="Engineering challenge and evaluation platform")
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.on_event("startup")
def startup():
 Base.metadata.create_all(bind=engine)
 seed()

@app.get("/health")
def health(): return {"status":"ok","service":"forgeeval"}

@app.get("/ready")
def ready():
 from sqlalchemy import text
 from app.core.db import SessionLocal
 with SessionLocal() as db: db.execute(text("SELECT 1"))
 return {"status":"ready"}
