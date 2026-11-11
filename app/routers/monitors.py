from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.security import require_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])


def _get_monitor(db: Session, monitor_id: int) -> models.Monitor:
    monitor = db.get(models.Monitor, monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.post("/monitors", response_model=schemas.MonitorOut, status_code=201)
def create_monitor(payload: schemas.MonitorCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Monitor).where(models.Monitor.name == payload.name)):
        raise HTTPException(status_code=409, detail="Monitor name already exists")
    data = payload.model_dump()
    data["target_url"] = str(payload.target_url)
    monitor = models.Monitor(**data)
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.get("/monitors", response_model=list[schemas.MonitorOut])
def list_monitors(db: Session = Depends(get_db)):
    return db.scalars(select(models.Monitor).order_by(models.Monitor.id)).all()


@router.get("/monitors/{monitor_id}", response_model=schemas.MonitorOut)
def get_monitor(monitor_id: int, db: Session = Depends(get_db)):
    return _get_monitor(db, monitor_id)


@router.patch("/monitors/{monitor_id}", response_model=schemas.MonitorOut)
def update_monitor(monitor_id: int, payload: schemas.MonitorUpdate, db: Session = Depends(get_db)):
    monitor = _get_monitor(db, monitor_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(monitor, field, str(value) if field == "target_url" else value)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.delete("/monitors/{monitor_id}", status_code=204)
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    db.delete(_get_monitor(db, monitor_id))
    db.commit()
    return Response(status_code=204)


@router.post("/monitors/{monitor_id}/metrics", response_model=schemas.MetricOut, status_code=201)
def ingest_metric(monitor_id: int, payload: schemas.MetricIn, db: Session = Depends(get_db)):
    monitor = _get_monitor(db, monitor_id)
    up = payload.status_code < 500
    metric = models.Metric(monitor_id=monitor.id, latency_ms=payload.latency_ms, status_code=payload.status_code, up=up)
    db.add(metric)
    if not up:
        db.add(models.Alert(monitor_id=monitor.id, severity="critical", message=f"{monitor.name} down: HTTP {payload.status_code}"))
    elif payload.latency_ms > settings.alert_latency_ms:
        db.add(models.Alert(monitor_id=monitor.id, severity="warning", message=f"{monitor.name} slow: {payload.latency_ms:.0f} ms"))
    db.commit()
    db.refresh(metric)
    return metric


@router.get("/monitors/{monitor_id}/metrics", response_model=list[schemas.MetricOut])
def list_metrics(monitor_id: int, limit: int = 100, db: Session = Depends(get_db)):
    _get_monitor(db, monitor_id)
    limit = max(1, min(limit, 1000))
    stmt = (
        select(models.Metric)
        .where(models.Metric.monitor_id == monitor_id)
        .order_by(models.Metric.recorded_at.desc(), models.Metric.id.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


@router.get("/alerts", response_model=list[schemas.AlertOut])
def list_alerts(resolved: bool | None = None, db: Session = Depends(get_db)):
    stmt = select(models.Alert).order_by(models.Alert.id.desc())
    if resolved is not None:
        stmt = stmt.where(models.Alert.resolved == resolved)
    return db.scalars(stmt).all()
