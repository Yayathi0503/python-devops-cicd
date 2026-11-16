pipeline {
    agent { label 'linux-docker' }

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }
        stage('Check tools') {
            steps {
                sh 'python3 --version && docker info > /dev/null'
                sh 'python3 scripts/jenkins_container.py cleanup'
            }
        }
        stage('Install and test') {
            steps {
                dir('task-management-api') {
                    sh '''
                        python3 -m venv .venv
                        .venv/bin/python -m pip install -r requirements-lock.txt
                        .venv/bin/python -m pytest -q --junitxml=test-results.xml
                    '''
                }
            }
        }
        stage('Build container') {
            steps {
                sh 'mkdir -p .ci && docker build --iidfile .ci/image.id task-management-api'
            }
        }
        stage('Smoke test') {
            steps {
                sh 'python3 scripts/jenkins_container.py smoke'
            }
        }
    }

    post {
        always {
            sh 'if [ -f scripts/jenkins_container.py ]; then python3 scripts/jenkins_container.py cleanup; fi'
            junit allowEmptyResults: true, testResults: 'task-management-api/test-results.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: '.ci/container.log'
        }
    }
}
