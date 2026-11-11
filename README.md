# PulseWatch

Cloud-native uptime and metrics monitoring platform.

- Backend: FastAPI (Python 3.12)
- Storage: SQLAlchemy (SQLite for dev, PostgreSQL in prod)
- Packaging: Docker + docker-compose
- CI/CD: GitHub Actions (lint, test, image build)

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Liveness |
| GET | /ready | Readiness (DB check) |
| POST/GET | /api/v1/monitors | Create/list monitors |
| GET/PATCH/DELETE | /api/v1/monitors/{id} | Manage monitor |
| POST/GET | /api/v1/monitors/{id}/metrics | Ingest/query samples |
| GET | /api/v1/alerts | List alerts |
| GET | /metrics | Prometheus exposition |
