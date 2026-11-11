from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_url: HttpUrl
    interval_seconds: int = Field(default=60, ge=10, le=3600)
    enabled: bool = True


class MonitorUpdate(BaseModel):
    target_url: HttpUrl | None = None
    interval_seconds: int | None = Field(default=None, ge=10, le=3600)
    enabled: bool | None = None


class MonitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    target_url: str
    interval_seconds: int
    enabled: bool
    created_at: datetime


class MetricIn(BaseModel):
    latency_ms: float = Field(ge=0)
    status_code: int = Field(ge=100, le=599)


class MetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    monitor_id: int
    latency_ms: float
    status_code: int
    up: bool
    recorded_at: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    monitor_id: int
    severity: str
    message: str
    resolved: bool
    created_at: datetime
