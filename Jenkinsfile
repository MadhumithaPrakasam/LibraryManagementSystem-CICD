pipeline {
agent any

environment {
    DOCKER = 'C:\\Users\\pm
adh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
    APP_IMAGE = 'library-management-system'
    ANSIBLE_IMAGE = 'library-ansible-runner'
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

    stage('Build Docker Image') {
        steps {
            bat '"%DOCKER%" build -t %APP_IMAGE%:%BUILD_NUMBER% .'
        }
    }

    stage('Automated Tests') {
        steps {
            bat '"%DOCKER%" run --rm %APP_IMAGE%:%BUILD_NUMBER% python -m pytest -q tests'
        }
    }

    stage('Build Ansible Runner') {
        steps {
            bat '"%DOCKER%" build -t %ANSIBLE_IMAGE% -f ansible/Dockerfile .'
        }
    }

    stage('Deploy with Ansible') {
        steps {
            bat '''
                "%DOCKER%" run --rm ^
                  -v "%WORKSPACE%:/workspace" ^
                  -v //./pipe/docker_engine:/var/run/docker.sock ^
                  -w /workspace ^
                  %ANSIBLE_IMAGE% ^
                  ansible-playbook -i ansible/inventory.ini ansible/deploy.yml -e app_image=%APP_IMAGE%:%BUILD_NUMBER%
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
        echo 'CI/CD pipeline with Docker and Ansible completed successfully!'
    }
    failure {
        echo 'Pipeline failed. Check Console Output for details.'
    }
}

}