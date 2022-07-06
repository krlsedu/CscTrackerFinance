#!groovy

pipeline {
  agent none
  stages {
    stage('Docker image') {
      agent any
      steps {
        sh 'docker build -t krlsedu/csctracker-finance:latest .'
      }
    }
    stage('Docker Push') {
      agent any
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
          sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword}"
          sh 'docker push krlsedu/csctracker-finance'
        }
      }
    }
  }
}