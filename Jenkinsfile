pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest tests/unit --cov=app --cov-branch \
                        --cov-report=xml --junitxml=unit-results.xml
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest tests/integration --cov=app --cov-branch --cov-append \
                        --cov-report=xml --junitxml=integration-results.xml
                '''
            }
        }

        stage('Start Application') {
            steps {
                sh '''
                    . .venv/bin/activate
                    nohup python run.py > app.log 2>&1 &
                    sleep 3
                '''
            }
        }

        stage('E2E Tests') {
            steps {
                // Runs against the selenium/standalone-chrome container
                // defined in docker/docker-compose.yml.
                sh '''
                    . .venv/bin/activate
                    python -m pytest tests/e2e --junitxml=e2e-results.xml -v
                '''
            }
        }

        stage('Coverage / Reports') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m coverage report
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                junit '**/*-results.xml'
                archiveArtifacts artifacts: 'coverage.xml, app.log', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            sh 'pkill -f "python run.py" || true'
        }
    }
}
