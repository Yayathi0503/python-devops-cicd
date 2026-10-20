# Automated CI Pipeline and Containerized Python Application

**Portfolio starter project — local Python API, tests, GitHub Actions CI, Docker and optional local Kubernetes.**

> This educational project uses synthetic examples. The workflow implements continuous integration, including container smoke tests; it does not deploy to production.

## Architecture

```text
Developer -> GitHub -> GitHub Actions -> Pytest + Docker build
                                      |
                                      v
                           Local Docker image (manual)
                                      |
                                      v
                         Optional kind Kubernetes cluster
                                      |
                            API /health and /metrics/
```

## Stack
Python 3.12, FastAPI, SQLAlchemy, SQLite, scikit-learn (synthetic-data demo), Pytest, GitHub Actions, Docker, Kubernetes (kind), Prometheus-compatible metrics.

## Getting started — Windows 11 PowerShell

Open this repository folder in VS Code, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train_model.py
python -m pytest -q
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs and http://127.0.0.1:8000/health. The browser should show `{"status":"ok"}` at `/health`.

### API examples

`POST /students` with JSON:

```json
{"name":"Demo Student","attendance":82,"marks":76,"assignment_score":88}
```

Then test `GET /students`, `PUT /students/{id}`, `GET /reports/summary`, and `DELETE /students/{id}` in `/docs`. The `/predict` endpoint uses a model trained on **synthetic** student examples only.

## Docker (Docker Desktop required)

From the repo root:

```powershell
docker build -t python-devops-cicd:local .
docker run --rm -p 8000:8000 python-devops-cicd:local
```

Validate http://127.0.0.1:8000/health. Stop the container with Ctrl+C.

## GitHub Actions CI

The workflow in `.github/workflows/ci.yml` runs on push and pull requests. It installs dependencies, runs tests, and builds an image (it **does not** publish or deploy the image). Check the repository's **Actions** tab for actual run results.

## Local Kubernetes (optional)

Requires Docker Desktop, `kind`, and `kubectl`.

```powershell
kind create cluster --name python-devops-demo
kind load docker-image python-devops-cicd:local --name python-devops-demo
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/student-analytics
kubectl port-forward service/student-analytics 8000:8000
```

After checking `/health`, stop port forwarding with Ctrl+C and clean up:

```powershell
kind delete cluster --name python-devops-demo
```

**Important:** Kubernetes is configured with a single replica. Local SQLite is not suitable for multiple independent replicas; move to a shared database before scaling.

## Monitoring

The app exposes Prometheus-compatible metrics at `/metrics/`. `monitoring/prometheus.yml` is a sample scrape configuration, **not** a running Grafana dashboard. Adjust targets to your Docker/Prometheus networking before use.

## Security and limitations

- Do not upload real student records. Demo lacks authentication and authorization.
- Do not commit secrets, `.env`, generated models, or databases.
- The synthetic ML model is for code integration only, not actual academic predictions.
- Cloud deployment, automated production CD, Helm, Prometheus/Grafana installation, and AWS are **not** implemented.
- Record actual results and errors in the README before calling this a completed resume project.

## Portfolio evidence checklist

- [x] Local Python 3.12 tests: 6 passed (20 October 2026)
- [x] Container `/health`, `/metrics/`, and `/predict` returned HTTP 200
- [x] Docker build and run verified on Docker Desktop
- [ ] GitHub Actions build green after push
- [x] Kubernetes rollout and in-cluster health endpoint verified on Docker Desktop (20 October 2026)
- [ ] Screenshots added to `docs/screenshots/` (optional)

## Resume description

*Implemented a FastAPI demonstration API with SQLite CRUD operations, input validation, Prometheus-compatible metrics, six automated tests, and a Docker container with a synthetic-data prediction endpoint. Added GitHub Actions CI and local Kubernetes manifests.*

## Verified environment

Validation on 20 October 2026: Windows 11, Python 3.12, Docker Desktop engine 29.8.2, and local Kubernetes 1.36.1. The API was deployed in an isolated local namespace with one ready replica. The kind commands above are provided as an alternative; kind itself was not used for this validation.

See [validation notes](docs/validation.md). SQLite data is ephemeral in this demo; a pod replacement can discard records.
