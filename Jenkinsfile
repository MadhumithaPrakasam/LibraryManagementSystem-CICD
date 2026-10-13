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

    stage('Deploy') {
        steps {
            bat '"%DOCKER%" volume create library_data'
            bat '"%DOCKER%" rm -f library-management-app'
            bat '"%DOCKER%" run -d --name library-management-app -p 5001:5000 -v library_data:/app/data library-management-system:%BUILD_NUMBER%'
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
        echo 'CI/CD pipeline completed successfully!'
    }
    failure {
        echo 'Pipeline failed. Check Console Output for details.'
    }
}

}