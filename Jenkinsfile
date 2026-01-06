pipeline {
    agent any 

    environment {
        DOCKER_USER = 'antonpas210'
        IMAGE_NAME = 'url-shortener'
        REGISTRY_CREDENTIALS_ID = 'docker-hub-credentials' 
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building Docker Image...'
                sh "docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest ."
            }
        }

        stage('Test') {
            steps {
                echo 'Linting Helm Chart...'
                sh "helm lint ./flask-app-chart"
                echo 'Testing Docker Image...'
                sh "docker run --rm ${DOCKER_USER}/${IMAGE_NAME}:latest python -m flask --version"
            }
        }

        stage('Deploy') {
            steps {
                echo 'Pushing to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS_ID}", passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh "echo $PASS | docker login -u $USER --password-stdin"
                    sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:latest"
                }

                echo 'Deploying to Kubernetes via Helm...'
                sh "helm upgrade --install flask-app ./flask-app-chart --set image.tag=latest"
            }
        }
    }
}
