# Verification — 21 October 2026

## Completed locally

- Windows 11, WSL 2, virtualization, and Docker Desktop engine 29.8.2 verified.
- Python 3.12, Git, VS Code, kubectl, Minikube, AWS CLI 2.38.1, and Terraform 1.16.6 installed.
- Pytest: 14 tests passed, including CRUD, invalid JSON and fields, missing records, persistence across app recreation, and metrics.
- Docker build succeeded. Live CRUD smoke test passed on localhost:8080.
- A test task survived a Docker container restart and was then removed.
- Dedicated Minikube `task-project` cluster: Kubernetes v1.36.0, 2 CPUs, 2200 MB memory.
- Kubernetes deployment rolled out successfully; one ready pod and a bound 1 GiB persistent volume claim. Live CRUD smoke test passed on localhost:8082.
- Terraform init and validate succeeded. Reviewed and applied a plan creating exactly one local Docker container and one data volume. Live CRUD smoke test passed on localhost:8083.
- Prometheus reported the task-api scrape target `up` with no error.
- Grafana health check reported database `ok`; provisioned `Task Management API` dashboard was returned by its API.

## GitHub

- Published on branch `codex/task-management-api` in `Yayathi0503/python-devops-cicd`, under `task-management-api/`.
- GitHub Actions Task API tests and container run passed: https://github.com/Yayathi0503/python-devops-cicd/actions/runs/39545715812
- The existing student API workflow also passed: https://github.com/Yayathi0503/python-devops-cicd/actions/runs/39545715769
- Pull-request creation is pending because the connector denied write access. The branch is published; no merge was performed.

## Pending external stages

- AWS cloud deployment is not performed. No AWS resources or credentials are configured by this project.

## Reproduce

Run `python -m pytest -q` using the project virtual environment, then `python smoke_test.py http://localhost:8080` against a running container. Replace port 8080 with 8082 or 8083 for the Kubernetes and Terraform copies.

Monitoring verification is operational (service API and scrape results); no visual screenshot review was performed. This project has no authentication and is intended for local practice.
