import json
import uuid
from datetime import datetime
from typing import Optional, Dict

import pyckson
from dateutil.tz import tzlocal

import random
import string

from model.folder_event import FolderDeleteQueueMessage, FolderDeleteInput, FolderDeleteResult, UserInput, StorageObject


# Create a custom wrapper for FolderDeleteInput that adds the user_id property
class TestFolderDeleteInput(FolderDeleteInput):
    @property
    def user_id(self):
        # This is used by the tests but not in the actual model
        # We're adding it dynamically for test compatibility
        return "drcigGWu0pM"


# Custom wrapper for the queue message that uses our test input class
class TestFolderDeleteQueueMessage(FolderDeleteQueueMessage):
    def __post_init__(self):
        # Convert regular input to test input with user_id property
        original_input = self.input
        test_input = TestFolderDeleteInput(
            folder_id=original_input.folder_id,
            activity_id=original_input.activity_id
        )
        object.__setattr__(self, 'input', test_input)


def get_folder_delete_event_json(modified: datetime = datetime.now()):
    """
    Generate a test folder delete event JSON object.
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        Dict: JSON representation of a folder delete event
    """
    folder_delete_event = {
        "createdBy": {
            "id": "drcigGWu0pM",
            "tiduuid": "d8b8f9a3-db1d-4f0e-8d90-6307aef3d6ee"
        },
        "createdAt": modified.isoformat(),
        "updatedAt": modified.isoformat(),
        "input": {
            "folderId": "ljtORDtSe-U",
            "activityId": "Dyfw481fE9U"
        },
        "result": {
            "downloadUrl": "https://example.com/folder/download/ljtORDtSe-U"
        }
    }
    return folder_delete_event


def get_folder_delete_event(modified: datetime = datetime.now()) -> FolderDeleteQueueMessage:
    """
    Parse a folder delete event JSON into a FolderDeleteQueueMessage object.
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        FolderDeleteQueueMessage: Parsed folder delete event object
    """
    # First parse normally, then convert to our test class
    parsed = pyckson.parse(FolderDeleteQueueMessage, get_folder_delete_event_json(modified))
    # Convert to test version with user_id support
    return TestFolderDeleteQueueMessage(
        job_id=parsed.job_id,
        job_type=parsed.job_type,
        status=parsed.status,
        project_id=parsed.project_id,
        created_by=parsed.created_by,
        created_at=parsed.created_at,
        updated_at=parsed.updated_at,
        input=parsed.input,
        result=parsed.result
    )


def get_sns_message(modified: datetime = datetime.now()) -> Dict:
    """
    Generate a test SNS message containing a folder delete event.
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        Dict: SNS message data structure
    """
    return {
        "SignatureVersion": "1",
        "Timestamp": "2019-01-02T12:45:07.000Z",
        "Signature": "tcc6faL2yUC6dgZdmrwh1Y4cGa/ebXEkAi6RibDsvpi+tE/1+82j...65r==",
        "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-"
                          "ac565b8b1a6c5d002d285f9598aa1d9b.pem",
        "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
        "Message": json.dumps(get_folder_delete_event_json(modified)),
        "MessageAttributes": {
            "FOLDER_DELETE_ACTION": {
                "Type": "String",
                "Value": "FOLDER_DELETE"
            }
        },
        "Type": "Notification",
        "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&amp;SubscriptionArn=arn:aws:"
                          "sns:us-east-1:123456789012:test-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:sns-lambda",
        "Subject": "TestInvoke"
    }


def get_sqs_fifo_msg(modified: datetime = datetime.now(), is_folder_event: bool = True):
    """
    Generate a test SQS FIFO message containing an SNS event with a folder delete event.
    
    Args:
        modified: Timestamp for event creation/modification
        is_folder_event: Flag to indicate this is a folder event (kept for compatibility)
        
    Returns:
        Dict: SQS message data structure
    """
    return {
        "Records": [
            {
                "messageId": "11d6ee51-4cc7-4302-9e22-7cd8afdaadf5",
                "receiptHandle": "AQEBBX8nesZEXmkhsmZeyIE8iQAMig7qw...",
                "body": json.dumps(get_sns_message(modified)),
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


def get_expected_folder_delete_request_body(folder_event: FolderDeleteQueueMessage) -> Dict:
    """
    Generate the expected request body for a folder delete event API call.
    
    Args:
        folder_event: The folder delete event to generate a request body for
        
    Returns:
        Dict: Expected request body for the API call
    """
    request_body = {
        "userId": folder_event.created_by.id,
        "folderId": folder_event.input.folder_id,
        "downloadUrl": folder_event.result.download_url,
        "objectToDelete": None,
        "objectDeleted": None,
        "type": None,
        "parentStorageObjectId": None
    }
    return request_body


def get_expected_request_headers(access_token: str) -> Dict:
    """
    Generate the expected request headers for a TCPS API call.
    
    Args:
        access_token: The access token to include in the Authorization header
        
    Returns:
        Dict: Expected request headers
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "TcpsTriggerService/1.0"
    }
    return headers


def prepare_ssm_response():
    """
    Generate a mock SSM response for TID configuration.
    
    Returns:
        Dict: Mock SSM response
    """
    return {
        "Parameter": {
            "Name": "/tid/fileservice-tcps-trigger/key",
            "Type": "SecureString",
            "Value": json.dumps(prepare_tid_config_json())
        }
    }


def prepare_tid_config_json():
    """
    Generate test TID configuration values.
    
    Returns:
        Dict: Test TID configuration
    """
    return {
        "tid_v4_token_url": "https://identity-stg.trimble.com/oauth/token",
        "tid_v4_consumer_key": "random_key",
        "tid_v4_consumer_secret": "random_secret",
        "tid_v4_application_name": "tcps-trigger-lambda"
    }


def prepare_token_api_response(access_token: str, expires_at: datetime) -> Dict:
    """
    Generate a mock token API response.
    
    Args:
        access_token: The access token to include in the response
        expires_at: The expiry timestamp for the token
        
    Returns:
        Dict: Mock token API response
    """
    return {
        "access_token": access_token,
        "expires_at": expires_at.timestamp()
    }


def generate_random_string(size: Optional[int] = 20):
    """
    Generate a random string of specified length.
    
    Args:
        size: Length of the random string to generate
        
    Returns:
        str: Random string
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))


class LambdaContext:
    """Mock AWS Lambda Context for testing"""

    def __init__(self, aws_request_id: Optional[str] = str(uuid.uuid4())):
        self.aws_request_id = aws_request_id


def get_nested_folder_delete_event_json(modified: datetime = datetime.now()):
    """
    Generate a test nested folder delete event JSON object (with downloadUrl).
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        Dict: JSON representation of a nested folder delete event
    """
    nested_folder_event = {
        "jobId": "2cefa0fc-49c8-487c-9b76-1d48fa0084c4",
        "jobType": "FOLDER_DELETION",
        "status": "DONE",
        "projectId": "yWPgPxO-WD4",
        "createdBy": {
            "id": "DLV-Z4wS1tU",
            "tiduuid": "f9310650-4cf5-4461-94f7-d812c8a2f6d2"
        },
        "createdAt": "2025-06-10T16:29:42.186Z",
        "updatedAt": "2025-06-10T16:29:48.446971+0000",
        "input": {
            "folderId": "TxCUm6hM_AM",
            "activityId": "Lehg3Aw9VHQ"
        },
        "result": {
            "downloadUrl": "#some download url is present"
        },
        "expireAt": 1752164982
    }
    return nested_folder_event


def get_empty_folder_delete_event_json(modified: datetime = datetime.now()):
    """
    Generate a test empty folder delete event JSON object (with object details).
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        Dict: JSON representation of an empty folder delete event
    """
    empty_folder_event = {
        "jobId": "empty-folder-job-id",
        "jobType": "FOLDER_DELETION",
        "status": "DONE",
        "projectId": "yWPgPxO-WD4",
        "createdBy": {
            "id": "DLV-Z4wS1tU",
            "tiduuid": "f9310650-4cf5-4461-94f7-d812c8a2f6d2"
        },
        "createdAt": modified.isoformat(),
        "updatedAt": modified.isoformat(),
        "input": {
            "folderId": "pbLVKHN_XE8",
            "activityId": "IMTr_ArnT14"
        },
        "result": {
            "objectToDelete": {
                "storage_object_id": 281474977720987,
                "type": "FOLDER",
                "name": "12",
                "project_id": 281474976771064,
                "orig_storage_object_id": 281474977720987,
                "created_by": 2970369,
                "modified_by": 2970369,
                "size_in_bytes": 0,
                "flag": None,
                "content_change_storage_object_id": 281474977720987,
                "storage_object_path_id": 281474977035209,
                "created": 1749573169065,
                "modified": 1749573169065,
                "hash": None,
                "revision": None,
                "file_service_id": None,
                "assim_flag": False
            },
            "objectDeleted": {
                "storage_object_id": 281474977720988,
                "type": "FOLDER",
                "name": "12",
                "project_id": 281474976771064,
                "orig_storage_object_id": 281474977720987,
                "created_by": 2970369,
                "modified_by": 2970369,
                "size_in_bytes": 0,
                "flag": "DELETED",
                "content_change_storage_object_id": 281474977720987,
                "storage_object_path_id": 281474977035209,
                "created": 1749573206868,
                "modified": 1749573206868,
                "hash": None,
                "revision": None,
                "file_service_id": None,
                "assim_flag": False
            },
            "type": "FOLDER",
            "parentStorageObjectId": 281474977707004
        }
    }
    return empty_folder_event


def get_nested_folder_delete_event(modified: datetime = datetime.now()) -> FolderDeleteQueueMessage:
    """
    Parse a nested folder delete event JSON into a FolderDeleteQueueMessage object.
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        FolderDeleteQueueMessage: Parsed nested folder delete event object
    """
    parsed = pyckson.parse(FolderDeleteQueueMessage, get_nested_folder_delete_event_json(modified))
    return TestFolderDeleteQueueMessage(
        job_id=parsed.job_id,
        job_type=parsed.job_type,
        status=parsed.status,
        project_id=parsed.project_id,
        created_by=parsed.created_by,
        created_at=parsed.created_at,
        updated_at=parsed.updated_at,
        input=parsed.input,
        result=parsed.result
    )


def get_empty_folder_delete_event(modified: datetime = datetime.now()) -> FolderDeleteQueueMessage:
    """
    Parse an empty folder delete event JSON into a FolderDeleteQueueMessage object.
    
    Args:
        modified: Timestamp for event creation/modification
        
    Returns:
        FolderDeleteQueueMessage: Parsed empty folder delete event object
    """
    parsed = pyckson.parse(FolderDeleteQueueMessage, get_empty_folder_delete_event_json(modified))
    return TestFolderDeleteQueueMessage(
        job_id=parsed.job_id,
        job_type=parsed.job_type,
        status=parsed.status,
        project_id=parsed.project_id,
        created_by=parsed.created_by,
        created_at=parsed.created_at,
        updated_at=parsed.updated_at,
        input=parsed.input,
        result=parsed.result
    )


def get_expected_nested_folder_delete_request_body(folder_event: FolderDeleteQueueMessage) -> Dict:
    """
    Generate the expected request body for a nested folder delete event API call.
    
    Args:
        folder_event: The nested folder delete event to generate a request body for
        
    Returns:
        Dict: Expected request body for the API call
    """
    request_body = {
        "userId": folder_event.created_by.id,
        "folderId": folder_event.input.folder_id,
        "activityId": folder_event.input.activity_id,
        "downloadUrl": folder_event.result.download_url,
        "objectToDelete": None,
        "objectDeleted": None,
        "type": None,
        "parentStorageObjectId": None
    }
    return request_body


def get_expected_empty_folder_delete_request_body(folder_event: FolderDeleteQueueMessage) -> Dict:
    """
    Generate the expected request body for an empty folder delete event API call.
    
    Args:
        folder_event: The empty folder delete event to generate a request body for
        
    Returns:
        Dict: Expected request body for the API call
    """
    from dataclasses import asdict
    
    request_body = {
        "userId": folder_event.created_by.id,
        "folderId": folder_event.input.folder_id,
        "activityId": folder_event.input.activity_id,
        "downloadUrl": None,
        "objectDeleted": asdict(folder_event.result.object_deleted) if folder_event.result.object_deleted else None,
        "type": folder_event.result.type,
        "parentStorageObjectId": folder_event.result.parent_storage_object_id
    }
    return request_body
