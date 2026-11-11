from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db
from app.routers import monitors


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="PulseWatch", version="0.1.0", lifespan=lifespan)
app.include_router(monitors.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(models.Monitor.id))) or 0
    open_alerts = db.scalar(select(func.count(models.Alert.id)).where(models.Alert.resolved.is_(False))) or 0
    return (
        "# TYPE pulsewatch_monitors_total gauge\n"
        f"pulsewatch_monitors_total {total}\n"
        "# TYPE pulsewatch_open_alerts gauge\n"
        f"pulsewatch_open_alerts {open_alerts}\n"
    )
