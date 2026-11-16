# Jenkins pipeline for the Task Management API

The root `Jenkinsfile` checks out the repository, installs the pinned Python
dependencies, runs the API tests, builds a Docker image and tests the running
container with readiness and create/read/update/list/delete requests. Jenkins
publishes JUnit results and archives the container log, including on failure.

## Set up the job

1. Use a Jenkins controller with Pipeline, Pipeline: Declarative, Git and JUnit
   plugins. Use a dedicated Linux agent with Git, Python 3.12, `venv`, pip and
   permission to use its Docker engine. Give that agent the `linux-docker` label.
2. Create a **Pipeline** job and choose **Pipeline script from SCM**, Git, repository
   `https://github.com/Yayathi0503/python-devops-cicd.git`, branch `*/main`, script
   path `Jenkinsfile`. Public read access needs no GitHub credential.
3. Select **Build Now**. Inspect the test report and archived `.ci/container.log`.
   A webhook is optional; this pipeline has no production deployment or registry
   push stage and needs no cloud credential.

The smoke test uses a random port bound only to `127.0.0.1`, so other jobs can use
the same agent without a fixed-port conflict. A `finally` block and Jenkins
`post` cleanup remove only the container recorded for this workspace. Build
concurrency is disabled for this job; retained build history is limited to ten
builds. Image layers remain in Docker's build cache.

## Run the same checks locally

From the repository root on Linux (activate a Python 3.12 environment first):

```sh
python -m pip install -r task-management-api/requirements-lock.txt
(cd task-management-api && python -m pytest -q --junitxml=test-results.xml)
mkdir -p .ci
docker build --iidfile .ci/image.id task-management-api
python scripts/jenkins_container.py smoke
```

The Python helper also works on Windows with Docker Desktop. The Jenkins job
itself uses Linux shell steps. A Jenkins execution requires an actual configured
controller and agent; local checks alone are not a recorded Jenkins build.

Reference: [Jenkins Declarative Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/).
