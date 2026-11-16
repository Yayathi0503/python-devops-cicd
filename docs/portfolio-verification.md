# Jenkins and AWS monitoring verification

Checked on 16 November 2026 using Windows 11, Python 3.12, Docker Desktop and
Terraform 1.16.6 with AWS provider 6.73.0.

## Completed locally

- Task Management API: **14 Pytest cases passed**, with JUnit XML output.
- Docker image built from `task-management-api/Dockerfile`.
- The Jenkins container helper started that image on an ephemeral loopback
  port and passed readiness plus create/read/update/list/delete requests.
- The helper collected the server log and removed its test container.
- `terraform fmt -check -recursive` and `terraform validate` passed.
- `terraform test`: **4 tests passed** using a mocked AWS provider. Coverage
  includes dashboard layout, EC2 dimensions/region, five-minute periods, alarm
  behavior, seven-day log retention, custom SNS settings and invalid inputs.
- `git diff --check` passed.

## Reproducible CI

`.github/workflows/portfolio.yml` runs the API/container checks and Terraform
validation on relevant pushes and pull requests. It retains the test report and
container log as a downloadable artifact. See the repository's Actions tab for
the actual run result; this workflow runs the Jenkins commands on GitHub Actions,
not inside a Jenkins controller.

## Requires a configured external environment

- A Jenkins controller/agent execution is not recorded. Configure the
  `linux-docker` agent and SCM job as described in [Jenkins setup](jenkins.md).
- No AWS resources were created. The Terraform tests mock AWS calls and require
  no cloud credentials. An existing EC2 ID, an authorized AWS identity and
  `terraform apply` are needed for a live dashboard.
- EC2-to-CloudWatch log delivery, live metric data, alarm transitions and SNS
  delivery remain deployment checks. No screenshot or live AWS result is claimed.

Resume wording should describe the pipeline and Terraform implementation,
automated tests and local container verification. It should not claim a completed
AWS deployment or a successful Jenkins server run without that evidence.
