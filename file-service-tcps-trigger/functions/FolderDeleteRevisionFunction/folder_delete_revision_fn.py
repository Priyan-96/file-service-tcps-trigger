"""
This module consists of the lambda handler function.
The Lambda function handler is the method in your function code that processes events.
"""
import json
import logging as log
from typing import Dict

import pyckson
import os
import requests

from model.folder_event import FolderDeleteQueueMessage
from folder_delete_revision_service import FolderDeleteRevisionService
from tcps_common.utils import logging_utils
from tcps_common.utils.api_client import ApiError

# x-ray tracing configuration
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(('requests',))

folder_delete_revision_service = FolderDeleteRevisionService()

def handler(event, context):
    """
    When your function is invoked, Lambda runs the handler method.
    When the handler exits or returns a response, it becomes available to handle another event.
    @param event: sqs event
    @param context: consists of lambda context information like requestId
    """
    # Get AWS lambda request id
    request_id = context.aws_request_id
    # Update logger with awsRequestId and json formatting
    logging_utils.update_logger_format(request_id=request_id)
    try:
        # Perform Folder Delete Revision on each record sequentially
        for record in event['Records']:
            # Convert sns event string to dict
            s_e: Dict = json.loads(record['body'])
            # Get folder event string from sns message
            folder_event_str: str = s_e['Message']
            # Convert the folder event string to FolderDeleteQueueMessage object
            folder_event: FolderDeleteQueueMessage = pyckson.parse(FolderDeleteQueueMessage, json.loads(folder_event_str))
            
            folder_delete_revision_service.invoke_tcps_api(folder_event)
    except (json.JSONDecodeError, KeyError) as parse_error:
        log.error(f"Failed to parse folder event: {str(parse_error)}")
        raise parse_error
    except ApiError as api_error:
        log.error(f"API call failed: {str(api_error)}")
        raise api_error
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        raise e 
    

