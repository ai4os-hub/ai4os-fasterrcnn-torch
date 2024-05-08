@Library(['github.com/indigo-dc/jenkins-pipeline-library@release/2.1.1']) _

def projectConfig

pipeline {
    agent any

    stages {
        stage('Application testing') {
            steps {
                //checkout scm *with* submodule
                checkout([
                    $class: 'GitSCM',
                    branches: scm.branches,
                    doGenerateSubmoduleConfigurations: true,
                    extensions: scm.extensions + [[$class: 'SubmoduleOption', parentCredentials: true]],
                    userRemoteConfigs: scm.userRemoteConfigs
                ])
                script {
                    projectConfig = pipelineConfig()
                    buildStages(projectConfig)
                }
            }
        }
    }
    post {
        // publish results and clean-up
        always {
            // file locations are defined in tox.ini
            // publish results of the style analysis
            recordIssues(enabledForFailure: true,
                         tools: [flake8(pattern: 'flake8.log',
                                 name: 'PEP8 report',
                                 id: "flake8_pylint")])
            // publish results of the coverage test
            publishHTML([allowMissing: false, 
                                 alwaysLinkToLastBuild: false, 
                                 keepAll: true, 
                                 reportDir: "htmlcov", 
                                 reportFiles: 'index.html', 
                                 reportName: 'Coverage report', 
                                 reportTitles: ''])
            // publish results of the security check
            publishHTML([allowMissing: false, 
                         alwaysLinkToLastBuild: false, 
                         keepAll: true, 
                         reportDir: "bandit", 
                         reportFiles: 'index.html', 
                         reportName: 'Bandit report', 
                         reportTitles: ''])
            // Clean after build
            cleanWs()
        }
    }
}

