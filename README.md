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
python -m pytest -q
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

## Project links

- Linear project: [P-SHI-6 PulseWatch Monitoring Platform](https://linear.app/shiperr/project/pulsewatch-monitoring-platform-6bfad243e67e) (issues SHI-8 to SHI-35)
- Notion docs: [PulseWatch Engineering Docs](https://app.notion.com/p/41598e0d458d81ac91b9c76524b0f90f)
- Open PRs: [#1 tests](https://github.com/naninetha05/pulsewatch-monitoring/pull/1), [#2 Docker](https://github.com/naninetha05/pulsewatch-monitoring/pull/2), [#3 CI/CD](https://github.com/naninetha05/pulsewatch-monitoring/pull/3)
