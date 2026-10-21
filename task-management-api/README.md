# Task Management API — Python and DevOps

A local portfolio project: Flask REST API, SQLite persistence, Pytest, Docker, Minikube Kubernetes, and a GitHub Actions test/build workflow.

## Start with Docker

Open this folder in VS Code, then open Terminal → New Terminal:

```powershell
docker compose up -d --build
```

Open http://localhost:8080/health. The response should be `{"status":"ok"}`.

## Try the API in PowerShell

```powershell
$task = Invoke-RestMethod http://localhost:8080/tasks -Method Post -ContentType 'application/json' -Body '{"title":"Learn Docker","description":"Build and run my first API"}'
Invoke-RestMethod http://localhost:8080/tasks
Invoke-RestMethod "http://localhost:8080/tasks/$($task.id)" -Method Patch -ContentType 'application/json' -Body '{"status":"done"}'
Invoke-RestMethod "http://localhost:8080/tasks/$($task.id)" -Method Delete
```

Endpoints: `GET /tasks`, `POST /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`. Status values: `todo`, `in_progress`, `done`. A title is required and must be 1–200 characters. `/health` is the process health check; `/ready` checks database access.

## Develop without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8081 --call app:create_app
```

The Python version saves data in `data/tasks.db`. Docker uses its own named volume. Kubernetes uses its own persistent volume. These three environments do not share task data.

## Deploy locally to Kubernetes

Docker Desktop must be running with Linux containers. This cluster uses about 2.2 GB of RAM, so close unnecessary applications on an 8 GB computer.

```powershell
$minikube = 'C:\Program Files\Kubernetes\Minikube\minikube.exe'
& $minikube start -p task-project --driver=docker --cpus=2 --memory=2200 --kubernetes-version=v1.36.0
docker build -t task-management-api:local .
& $minikube -p task-project image load task-management-api:local
kubectl --context task-project apply -f k8s/local.yaml
kubectl --context task-project -n task-project rollout status deployment/task-api --timeout=180s
kubectl --context task-project -n task-project port-forward service/task-api 8082:8080 --address=127.0.0.1
```

Keep the last terminal open and visit http://localhost:8082/health. Press Ctrl+C to stop forwarding. The Deployment uses one replica and Recreate updates because this educational version uses a single SQLite database. Use PostgreSQL before scaling to multiple replicas.

## Optional monitoring

```powershell
docker compose --profile monitoring up -d --build
```

Open http://localhost:3000/d/task-api for the provisioned Grafana dashboard. Prometheus is at http://localhost:9090 and API metrics are at http://localhost:8080/metrics. The dashboard monitors the Compose API on port 8080, not the Kubernetes or Terraform copy. Generate requests with the API commands above and allow about 20 seconds for collection. Metrics reset when the API restarts; monitoring history is disposable in this local setup. Grafana permits anonymous read-only access and binds only to localhost.

## Stop and restart

```powershell
docker compose stop
docker compose --profile monitoring stop
& 'C:\Program Files\Kubernetes\Minikube\minikube.exe' stop -p task-project
```

Restart using `docker compose up -d` and the Minikube start command above. Stopping preserves data. `docker compose down -v` and deleting the Minikube cluster remove stored data; use those only when you intend to reset the project.

## GitHub and CI

The `.github/workflows/task-api.yml` (in the repository root) workflow tests the API and builds its image on pushes and pull requests. It does not publish images or deploy to AWS. A hosted run can only be verified after this folder is pushed to your chosen GitHub repository. Check your GitHub plan's Actions allowance before enabling hosted runs.

## AWS and Terraform

The `terraform/` folder provides a separate local infrastructure-as-code exercise. It creates one Docker container on port 8083 and a named data volume, using the image already built above. It has no AWS provider or cloud resources.

```powershell
$env:TF_VAR_image_id = docker image inspect task-management-api:local --format '{{.Id}}'
terraform -chdir=terraform init
terraform -chdir=terraform plan
terraform -chdir=terraform apply
```

Review the plan, then type `yes` if it lists only the local container and volume. Terraform's database is separate from Compose and Kubernetes. To remove the exercise, use `terraform -chdir=terraform destroy`; this deletes its task data too. Preserve the local state files and never commit them.

AWS CLI and Terraform are installed. This local project does not call AWS, store AWS credentials, create infrastructure, or incur AWS resource charges. Cloud deployment is a separate pending stage requiring a chosen account, region, reviewed cost estimate, and explicit approval to create billable resources. Do not describe this project as deployed on AWS until that work is completed. Budget alerts are notifications, not spending caps.

## Scope and learning notes

- Python: request validation, HTTP status codes, parameterized SQL, application factory, database lifecycle, tests.
- DevOps: container image, non-root runtime, health checks, persistent volumes, Kubernetes probes and resource limits, CI workflow.
- This API has no authentication and is intended for local learning. Local ports bind to loopback. Add authentication, authorization, TLS, migrations, backups, and operational monitoring before public deployment.
- Do not commit `.env`, AWS credentials, database files, Terraform state, or the virtual environment.

## Resume wording

Use only the parts verified in `VERIFICATION.md`:

"Built a Python Flask task-management REST API with SQLite persistence and 14 automated tests; deployed it locally with Docker and Kubernetes persistent storage, automated a separate local deployment with Terraform, and configured Prometheus/Grafana monitoring."

Do not claim a hosted CI run or AWS deployment until verified.

