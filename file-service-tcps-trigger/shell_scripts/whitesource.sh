#!/bin/bash

set -x

curl -LJO https://github.com/whitesource/fs-agent-distribution/raw/master/standAlone/whitesource-fs-agent.jar


verifySuccess () {
  scanType="$1"
  exitCode="$2"

  case "$exitCode" in
    0)  echo "$scanType completed successfully!"
        ;;
  255)  error="A general error has occurred in $scanType!"
        # ERROR: General error has occurred.
        ;;
  254)  policyRejectionSummary=$(find ./whitesource -name 'policyRejectionSummary.json')
        totalRejected=$(jq '(.summary.totalRejectedLibraries)' "$policyRejectionSummary")
        error="*$totalRejected policy violation(s) occurred in $scanType:*"
        error+=$'\n'
        error+=$(jq -r '.rejectingPolicies[] | .rejectedLibraries[] | "- *Dependency* \(.name) *used in* \(.manifestFile)\n"' $policyRejectionSummary)
        error+=$'\n\n'
        error+="*If there are any new violations, <https://jira.trimble.tools/secure/CreateIssue!default.jspa|please create a ticket in JIRA> to address the issue.*"
        # POLICY_VIOLATION:
        # One or more of the scanned components violates an Organization or Product level policy.
        # Policy summary reports are created and saved in the newly-created whitesource directory,
        # located under the current working directory ($pwd or %cd%).
        # Only applicable when configured to checkPolicies=true and forceUpdate=false.
        ;;
  253)  error="A client-side error has occurred in $scanType!"
        # CLIENT_FAILURE: Client-side error has occurred.
        ;;
  252)  error="The agent was unable to establish a connection to the WhiteSource application server in $scanType!"
        # CONNECTION_FAILURE:
        # The agent was unable to establish a connection to the WhiteSource application server
        # (e.g., due to a blocked Internet connection).
        ;;
  251)  error="A client-side error has occurred in $scanType!"
        # SERVER_FAILURE: Server-side error has occurred
        # (e.g., a malformed request or a request that cannot be parsed was received).
        ;;
    *)  error "An unknown error code ($exitCode) has occurred during $scanType!"
        ;;
  esac

    if [ -n "$error" ]
    then
        echo "AN ERROR OCCURRED!"
        echo "$error"

        message="*$bamboo_planName - Build#: $bamboo_buildNumber*"
        message+=$'\n\n'
        message+="$error"
        message+=$'\n\n'
        message+="<$bamboo_buildResultsUrl/artifact|WhiteSource scan log or report may contain more information.>"
        message+=$'\n\n'
        message+="*(EOM)*"

        payload=$(jq -n --arg msg "$message" '{ text: $msg }')
        curl -X POST -H "Content-Type: text/plain" --data "$payload" $bamboo_TcFsWSSChatWebHook
    fi
}

scanAndPublish () {
java -jar whitesource-fs-agent.jar -c ./wss.config -d ../functions/FileServiceTCPSTriggerFunction/ -apiKey ${bamboo_wssApiPassword} -productToken ${bamboo_wssProductPassword}
verifySuccess "WSS Report Upload" $?
}

scanAndPublish