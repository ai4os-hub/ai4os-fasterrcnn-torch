#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library@1.4.0']) _

def job_result_url = ''

ci_cd_image = 'mteamkit/cicd-python-gl'
ci_cd_image_registry = 'https://docker.io'

pipeline {
    agent {
        docker { 
            image "${ci_cd_image}"
            registryUrl "${ci_cd_image_registry}"
            registryCredentialsId 'indigobot'
        }
    }

    environment {
        author_name = "Fahimeh"
        author_email = "f.alibabaee@gmail.com"
        app_name = "fasterrcnn_pytorch_api"
        job_location = "Pipeline-as-code/DEEP-OC-org/DEEP-OC-fasterrcnn_pytorch_api/${env.BRANCH_NAME}"
    }

    stages {
        stage('Code fetching') {
            steps {
                //checkout scm
                checkout([
                    $class: 'GitSCM',
                    branches: scm.branches,
                    doGenerateSubmoduleConfigurations: true,
                    extensions: scm.extensions + [[$class: 'SubmoduleOption', parentCredentials: true]],
                    userRemoteConfigs: scm.userRemoteConfigs
                ])
            }
        }

        stage('Metrics gathering') {
            steps {
                //SLOCRun()
                sh "cloc --by-file --fullpath --not-match-d='(.tox|htmlcov|.egg-info)' --xml --out=cloc.xml ."
            }
            post {
                success {
                    SLOCPublish()
                }
            }
        }

        stage('Style analysis: PEP8') {
            steps {
                ToxEnvRun('qc.sty')
            }
        }

        stage('Unit testing with Coverage') {
            steps {
                ToxEnvRun('qc.cov')
            }
            post {
                success {
                    HTMLReport('htmlcov', 'index.html', 'Coverage report')
                }
            }
        }

        stage('Security scanner') {
            steps {
                ToxEnvRun('qc.sec')
                script {
                    if (currentBuild.result == 'FAILURE') {
                        currentBuild.result = 'UNSTABLE'
                    }
               }
            }
            post {
               always {
                    HTMLReport("bandit", 'index.html', 'Bandit report')
                }
            }
        }

        stage("Re-build Docker images") {
            when {
                anyOf {
                   branch 'master'
                   branch 'test'
                   buildingTag()
               }
            }
            steps {
                script {
                    def job_result = JenkinsBuildJob("${env.job_location}")
                    job_result_url = job_result.absoluteUrl
                }
            }
        }

    }

    post {
        // Clean after build (always delete .tox directory)
        always {
            cleanWs(cleanWhenNotBuilt: true,
                    deleteDirs: true,
                    notFailBuild: true,
                    patterns: [[pattern: '.tox', type: 'INCLUDE']])
        }
    }
}
