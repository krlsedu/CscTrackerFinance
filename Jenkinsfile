#!groovy
env.RELEASE_COMMIT = "1";
env.VERSION_NAME = "";

pipeline {
    agent none
    stages {
        stage('CheckBranch') {
            agent any
            steps {
                script {
                    result = sh(script: "git log -1 | grep 'Triggered Build'", returnStatus: true)
                    echo 'result ' + result
                    env.RELEASE_COMMIT = result == 0 ? '0' : '1'
                }
            }
        }
        stage('Gerar versão') {
            agent any
            when {
                expression { env.RELEASE_COMMIT != '0' }
            }
            steps {
                script {
                    echo 'RELEASE_COMMIT ' + env.RELEASE_COMMIT
                    if (env.BRANCH_NAME == 'master') {
                        echo 'Master'
                        VERSION = VersionNumber(versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}.${BUILD_WEEK,XX}.${BUILDS_THIS_WEEK,XXX}')
                    } else {
                        echo 'Dev'
                        VERSION = VersionNumber(versionNumberString: '${BUILD_DATE_FORMATTED, "yyyyMMdd"}.${BUILDS_TODAY}.${BUILD_NUMBER}')
                        VERSION = VERSION + '-SNAPSHOT'
                    }
                    env.VERSION_NAME = VERSION
                }
            }
        }
        stage('Docker image') {
            agent any
            when {
                expression { env.RELEASE_COMMIT != '0' }
            }
            steps {
                sh 'docker build -t krlsedu/csctracker-finance:' + env.VERSION_NAME + ' -t krlsedu/csctracker-finance:latest  .'
            }
        }

        stage('Docker Push') {
            agent any
            when {
                expression { env.RELEASE_COMMIT != '0' }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword}"
                    sh 'docker push krlsedu/csctracker-finance:' + env.VERSION_NAME
                    sh 'docker push krlsedu/csctracker-finance'
                }
            }
        }

        stage('Service update'){
            agent any
            when {
                expression { env.RELEASE_COMMIT != '0' }
            }
            steps{
                sh 'docker service update --image krlsedu/csctracker-finance:' + env.VERSION_NAME + ' csctracker_services_finance'
            }
        }
    }
}
