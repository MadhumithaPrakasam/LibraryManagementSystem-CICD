pipeline {
    agent any

    environment {
        DOCKER = 'C:\\Users\\pmadh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Docker') {
            steps {
                bat '"%DOCKER%" version'
            }
        }

        stage('Test WSL Access') {
            steps {
                bat 'wsl.exe -d Ubuntu -- bash -lc "whoami && ansible --version"'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER%" build -t library-management-system:%BUILD_NUMBER% .'
            }
        }

        stage('Automated Tests') {
            steps {
                bat '"%DOCKER%" run --rm library-management-system:%BUILD_NUMBER% python -m pytest -q tests'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                bat '''
                    wsl.exe -d Ubuntu -- bash -lc "cd /mnt/c/LibraryManagementSystem-CICD && ansible-playbook -i ansible/inventory.ini ansible/deploy.yml"
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                powershell '''
                    $response = Invoke-WebRequest -Uri "http://localhost:5001/health" -UseBasicParsing
                    if ($response.StatusCode -ne 200) {
                        throw "Application health check failed"
                    }
                    Write-Output $response.Content
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline with Ansible completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output for details.'
        }
    }
}