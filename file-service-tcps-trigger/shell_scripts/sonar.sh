#!/bin/bash
cd ../functions/ || exit
set -x
####### Variables
PROJECT_KEY="TrimbleConnect.Platform:TrimbleConnectFileServiceTCPSTriggerService"
PROJECT_NAME="TrimbleConnect - Platform - TrimbleConnect FileServiceTCPSTriggerService"
SONAR_URL="https://sonar.trimble.tools"
SONAR_SCANNER="/var/opt/sonar-scanner-4.3.0.2102-linux/bin/sonar-scanner"

####### Send Sonar project data (create/update project) to Sonar server
${SONAR_SCANNER}                          \
     -Dsonar.projectKey="$PROJECT_KEY"    \
     -Dsonar.projectName="$PROJECT_NAME"  \
     -Dsonar.host.url=${SONAR_URL}        \
     -Dsonar.sources="."                  \
     -Dsonar.branch.name=${bamboo_repository_git_branch}   \
     -Dsonar.exclusions=**/.env/**,**/tests/**,**/*.xml  \
     -Dsonar.login=${bamboo_sonarLoginPassword}


###### Find out if project failed in Sonar gate
passgate(){
	RESPONSE=$(curl -u ${bamboo_sonarLoginPassword}: ${SONAR_URL}/api/qualitygates/project_status?projectKey=$PROJECT_KEY)
	echo "$RESPONSE"

	if [[ "$RESPONSE" =~ '"status":"OK"' ]]; then
		echo "Gate successfully passed!"
		exit 0
	fi

	if [[ "$RESPONSE" =~ '"status":"NONE"' ]]; then
		echo "Gate not ready, take a nap."
		sleep 30
		passgate
	fi

	echo "Gate was not passed! Got Error."
	exit 1
}