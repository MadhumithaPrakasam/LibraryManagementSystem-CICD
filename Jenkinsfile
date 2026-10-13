pipeline {
  agent any
  environment {
    IMAGE_NAME = 'library-management-system'
    CONTAINER_NAME = 'library-management-app'
    DATA_VOLUME = 'library_data'
    APP_PORT = '5001'
  }
  options { timestamps(); disableConcurrentBuilds() }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build Docker Image') {
      steps {
        sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
        sh 'docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest'
      }
    }
    stage('Automated Tests') {
      steps { sh 'docker run --rm ${IMAGE_NAME}:${BUILD_NUMBER} python -m pytest -q tests' }
    }
    stage('Deploy') {
      steps {
        sh '''
          docker volume create ${DATA_VOLUME}
          docker rm -f ${CONTAINER_NAME} 2>/dev/null || true
          docker run -d --name ${CONTAINER_NAME} --restart unless-stopped -p ${APP_PORT}:5000 -v ${DATA_VOLUME}:/app/data ${IMAGE_NAME}:${BUILD_NUMBER}
        '''
      }
    }
    stage('Verify Deployment') {
      steps {
        sh 'sleep 3'
        sh 'docker ps --filter "name=${CONTAINER_NAME}"'
        sh 'docker exec ${CONTAINER_NAME} python -c "import urllib.request; print(urllib.request.urlopen(\'http://127.0.0.1:5000/health\').read().decode())"'
      }
    }
  }
  post {
    success { echo 'Library CI/CD completed successfully.' }
    failure { echo 'Pipeline failed. Check the failed stage logs.' }
  }
}
