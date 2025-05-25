import json
import uuid
from datetime import datetime
from typing import Optional, Dict

import pyckson
from dateutil.tz import tzlocal

import random
import string

from model.file_event import FileOrFolderEvent


def get_file_event_json(modified: datetime = datetime.now(), has_client_name: bool = False):
    file_event = {
        "eventType": "FILE_ADD",
        "correlationId": "73ad4588-9d26-44d3-bad0-ce285e23f44a",
        "eventTime": modified.isoformat(),
        "eventVersion": "1.0.0",
        "userIdentity": {
            "id": "drcigGWu0pM",
            "tiduuid": "d8b8f9a3-db1d-4f0e-8d90-6307aef3d6ee"
        },
        "objectData": {
            "id": "ljtORDtSe-U",
            "versionId": "ljtORDtSe-U",
            "type": "FILE",
            "projectId": "Rm6SfQd9h6Y",
            "parentId": "1UGd2qLss6w",
            "parentType": "FOLDER",
            "activityId": "Dyfw481fE9U",
            "processingPriority": "LOW",
            "clientName": "my.sketchup",
            "fileSize": 1290,
            "ecomTransactionId": "73ad4588-9d26-44d3-bad0-ce285e23f44a",
            "entitlementId": "3715da1f-60a0-4170-a8ed-9b529a6c3e7f",
            "tcfsSpaceId": "73ad4588-9d26-44d3-bad0-ce285e23f44a",
            "tcfsFileId": "f02fc476-655b-4c99-9bc2-6418afe5997f",
            "tcfsVersionId": "1.0"
        }
    }
    if has_client_name:
        file_event['objectData']['clientName'] = "test.my.sketchup"
    return file_event


def get_file_event(modified: datetime = datetime.now(), has_client_name: bool = False) -> FileOrFolderEvent:
    return pyckson.parse(FileOrFolderEvent, get_file_event_json(modified, has_client_name))


def get_folder_event_json(modified: datetime = datetime.now(), has_client_name: bool = False):
    folder_event = {
        "eventType": "FOLDER_UPDATE",
        "correlationId": "73ad4588-9d26-44d3-bad0-ce285e23f44a",
        "eventTime": modified.isoformat(),
        "eventVersion": "1.0.0",
        "userIdentity": {
            "id": "drcigGWu0pM",
            "tiduuid": "d8b8f9a3-db1d-4f0e-8d90-6307aef3d6ee"
        },
        "objectData": {
            "id": "ljtORDtSe-U",
            "versionId": "ljtORDtSe-U",
            "type": "FOLDER",
            "projectId": "Rm6SfQd9h6Y",
            "parentId": "1UGd2qLss6w",
            "parentType": "FOLDER",
            "activityId": "Dyfw481fE9U",
            "clientName": "my.sketchup",
            "oldParentId": "MxBN506S1pg",
            "oldName": "test",
            "moveRenameActivityId": "2ijzMPlJLFM",
            "oldVersionId": "uPg06fykGLI"
        }
    }
    if has_client_name:
        folder_event['objectData']['clientName'] = "test.my.sketchup"
    return folder_event


def get_folder_event(modified: datetime = datetime.now(), has_client_name: bool = False) -> FileOrFolderEvent:
    return pyckson.parse(FileOrFolderEvent, get_folder_event_json(modified, has_client_name))


def get_sns_message(modified: datetime = datetime.now(), is_folder_event: bool = False,
                    has_client_name: bool = False, is_file_permission_event: bool = False, is_folder_permission_event: bool = False) -> Dict:
    return {
        "SignatureVersion": "1",
        "Timestamp": "2019-01-02T12:45:07.000Z",
        "Signature": "tcc6faL2yUC6dgZdmrwh1Y4cGa/ebXEkAi6RibDsvpi+tE/1+82j...65r==",
        "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-"
                          "ac565b8b1a6c5d002d285f9598aa1d9b.pem",
        "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
        "Message": json.dumps(
            get_folder_permission_event_json(modified) if is_folder_permission_event
            else get_file_permission_event_json(modified) if is_file_permission_event
            else get_file_event_json(modified, has_client_name) if is_folder_event is False
            else get_folder_event_json(modified, has_client_name)
        ),
        "MessageAttributes": {
            "FILE_ASYNC_ACTION": {
                "Type": "String",
                "Value": "FILE_UPLOAD"
            }
        },
        "Type": "Notification",
        "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&amp;SubscriptionArn=arn:aws:"
                          "sns:us-east-1:123456789012:test-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:sns-lambda",
        "Subject": "TestInvoke"

    }


def get_sqs_fifo_msg(modified: datetime = datetime.now(), is_folder_event: bool = False, has_client_name: bool = False, is_file_permission_event: bool = False, is_folder_permission_event: bool = False):
    return {
        "Records": [
            {
                "messageId": "11d6ee51-4cc7-4302-9e22-7cd8afdaadf5",
                "receiptHandle": "AQEBBX8nesZEXmkhsmZeyIE8iQAMig7qw...",
                "body": json.dumps(get_sns_message(modified, is_folder_event, has_client_name, is_file_permission_event, is_folder_permission_event)),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1573251510774",
                    "SequenceNumber": "18849496460467696128",
                    "MessageGroupId": "1",
                    "SenderId": "AIDAIO23YVJENQZJOL4VO",
                    "MessageDeduplicationId": "1",
                    "ApproximateFirstReceiveTimestamp": "1573251510774"
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:fifo.fifo",
                "awsRegion": "us-east-1"
            }
        ]
    }


def get_expected_file_upload_request_body(modified: datetime, has_client_name: bool = False) -> Dict:
    file_event = get_file_event_json(modified, has_client_name)
    file_data = file_event['objectData']
    request_body = {
        "id": file_data['id'],
        "versionId": file_data['versionId'],
        "projectId": file_data['projectId'],
        "parentId": file_data['parentId'],
        "parentType": file_data['parentType'],
        "activityType": file_event['eventType'],
        "processingPriority": file_data['processingPriority'],
        "activityId": file_data['activityId'],
        "modifiedOn": str(file_event['eventTime']),
        "modifiedBy": {
            "id": file_event['userIdentity']['id'],
            "tiduuid": file_event['userIdentity']['tiduuid']
        },
        "correlationId": file_event['correlationId'],
        "moveRenameActivityId": None,
        "oldParentId": None,
        "oldName": None,
        "oldVersionId": None,
        "tcfsSpaceId": file_data['tcfsSpaceId'],
        "tcfsFileId": file_data['tcfsFileId'],
        "tcfsVersionId": file_data['tcfsVersionId']
    }
    if has_client_name is not None:
        request_body["clientName"] = file_data['clientName']
    return request_body


def get_expected_folder_update_request_body(modified: datetime, has_client_name: bool = False) -> Dict:
    folder_event = get_folder_event_json(modified, has_client_name)
    folder_data = folder_event['objectData']
    request_body = {
        "id": folder_data['id'],
        "versionId": folder_data['versionId'],
        "projectId": folder_data['projectId'],
        "parentId": folder_data['parentId'],
        "parentType": folder_data['parentType'],
        "activityType": folder_event['eventType'],
        "processingPriority": None,
        "activityId": folder_data['activityId'],
        "modifiedOn": str(folder_event['eventTime']),
        "modifiedBy": {
            "id": folder_event['userIdentity']['id'],
            "tiduuid": folder_event['userIdentity']['tiduuid']
        },
        "correlationId": folder_event['correlationId'],
        "moveRenameActivityId": folder_data['moveRenameActivityId'],
        "oldParentId": folder_data['oldParentId'],
        "oldName": folder_data['oldName'],
        "oldVersionId": folder_data['oldVersionId']
    }
    if has_client_name is not None:
        request_body["clientName"] = folder_data['clientName']
    return request_body


def get_expected_ecom_request_body(modified: datetime, has_client_name: bool = False) -> Dict:
    file_event = get_file_event_json(modified, has_client_name)
    file_data = file_event['objectData']
    request_body = {
        "id": file_data['ecomTransactionId'],
        "entitlementId": file_data['entitlementId'],
        "projectId": file_data['projectId'],
        "action": "FILE_ADD",
        "region": "na",
        "count": file_data['fileSize'],
        "status": "DONE",
        "createdBy": file_event['userIdentity']['tiduuid'],
        "modifiedBy": file_event['userIdentity']['tiduuid']
    }
    return request_body


def get_expected_request_headers(access_token: str) -> Dict:
    return {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
        "User-Agent": "TcpsTriggerService/1.0"
    }


def prepare_ssm_response():
    return {'Parameter': {'Name': '/test/common/tid', 'Type': 'String',
                          'Value': json.dumps(prepare_tid_config_json()), 'Version': 1,
                          'LastModifiedDate': datetime(2020, 4, 21, 16, 10, 52, 947000, tzinfo=tzlocal()),
                          'ARN': 'arn:aws:ssm:us-east-1:342542654:parameter/file-processor-service'},
            'ResponseMetadata': {'RequestId': 'f961b334-2209-4423-9579-9c65454297f4', 'HTTPStatusCode': 200,
                                 'HTTPHeaders': {'x-amzn-requestid': 'f961b334-2209-4423-9579-9c65454297f4',
                                                 'content-type': 'application/x-amz-json-1.1',
                                                 'content-length': '564', 'date': 'Tue, 05 May 2020 10:16:23 GMT'},
                                 'RetryAttempts': 0}}


def prepare_tid_config_json():
    return {
        "tid_v4_token_url": "https://stage.id.trimblecloud.com/oauth/token/",
        "tid_v4_consumer_key": "99084960-c700-44a6-9022-adcebcdc1380",
        "tid_v4_consumer_secret": "39bfdb9b-73bd-4929-b411-f8d4992ad66f",
        "tid_v4_application_name": "testAppName"
    }


def generate_random_string(size: Optional[int] = 20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))


def prepare_token_api_response(access_token: str, expires_at: datetime) -> Dict:
    return {
        'access_token': access_token,
        'expires_at': expires_at.timestamp()
    }

def get_file_permission_event_json(modified: datetime = datetime.now()):
    file_permission_event = {
        "eventType": "FILE_PERMISSION_CHANGE",
        "eventVersion": "1.0.0",
        "eventTime": modified.isoformat(),
        "correlationId": "a6399a4f-e0c8-4482-be69-b6332ba58071",
        "userIdentity": {
            "id": "drcigGWu0pM",
            "tiduuid": "d8b8f9a3-db1d-4f0e-8d90-6307aef3d6ee"
        },
        "fileFolderPermissionEventData": {
            "fileId": "eOeU9LEULa0",
            "projectId": "F52u-wg-BMs",
            "newlyAddedPermissions": [
                "ejcX_DWqItY",
                "d4wfMpaWQS8"
            ],
            "updatedPermissions": [],
            "removedPermissions": []
        }
    }
    return file_permission_event

def get_file_permission_event(modified: datetime = datetime.now()) -> FileOrFolderEvent:
    return pyckson.parse(FileOrFolderEvent, get_file_permission_event_json(modified))

def get_expected_file_permission_request_body(modified: datetime) -> Dict:
    file_permission_event = get_file_permission_event_json(modified)
    permission_data = file_permission_event["fileFolderPermissionEventData"]

    request_body = {
        "id": permission_data["fileId"],
        "projectId": permission_data["projectId"],
        "activityType": file_permission_event["eventType"],
        "modifiedOn": file_permission_event["eventTime"],
        "modifiedBy": {
            "id": file_permission_event['userIdentity']['id'],
            "tiduuid": file_permission_event['userIdentity']['tiduuid']
        },
        "correlationId": file_permission_event["correlationId"],
        "newlyAddedPermissions": permission_data["newlyAddedPermissions"],
        "updatedPermissions": permission_data["updatedPermissions"],
        "removedPermissions": permission_data["removedPermissions"]
    }
    return request_body

def get_folder_permission_event_json(modified: datetime = datetime.now()):
    folder_permission_event = {
        "eventType": "FOLDER_PERMISSION_CHANGE",
        "eventVersion": "1.0.0",
        "eventTime": modified.isoformat(),
        "correlationId": "f6a4c4c7-53a9-4b83-8e87-0e801e964bcc",
        "userIdentity": {
            "id": "drcigGWu0pM",
            "tiduuid": "d8b8f9a3-db1d-4f0e-8d90-6307aef3d6ee"
        },
        "fileFolderPermissionEventData": {
            "folderId": "TXast5SND48",
            "projectId": "8Qrg20YmZkE",
            "newlyAddedPermissions": [
                "ejcX_DWqItY",
                "d4wfMpaWQS8"
            ],
            "updatedPermissions": [],
            "removedPermissions": []
        }
    }
    return folder_permission_event

def get_folder_permission_event(modified: datetime = datetime.now()) -> FileOrFolderEvent:
    return pyckson.parse(FileOrFolderEvent, get_folder_permission_event_json(modified))

def get_expected_folder_permission_request_body(modified: datetime) -> Dict:
    folder_permission_event = get_folder_permission_event_json(modified)
    permission_data = folder_permission_event["fileFolderPermissionEventData"]

    return {
        "id": permission_data["folderId"],
        "projectId": permission_data["projectId"],
        "activityType": folder_permission_event["eventType"],
        "modifiedOn": folder_permission_event["eventTime"],
        "modifiedBy": {
            "id": folder_permission_event['userIdentity']['id'],
            "tiduuid": folder_permission_event['userIdentity']['tiduuid']
        },
        "correlationId": folder_permission_event["correlationId"],
        "newlyAddedPermissions": permission_data["newlyAddedPermissions"],
        "updatedPermissions": permission_data["updatedPermissions"],
        "removedPermissions": permission_data["removedPermissions"]
    }

class LambdaContext:

    def __init__(self, aws_request_id: Optional[str] = str(uuid.uuid4())):
        self.aws_request_id = aws_request_id
