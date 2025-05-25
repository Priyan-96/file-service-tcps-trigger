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

from model.f_event import FolderDeleteQueueMessage
from folder_delete_revision_service import FolderDeleteRevisionService
from utils import logging_utils

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
    log.info(f'Received message(s): {event} from SQS to process')
    try:
        # Perform Folder Delete Revision on each record sequentially
        for record in event['Records']:
            # Convert sns event string to dict
            sns_event: Dict = json.loads(record['body'])
            # Get folder event string from sns message
            f_event_str: str = sns_event['Message']
            # Convert the folder event string to FolderDeleteQueueMessage object
            f_event: FolderDeleteQueueMessage = pyckson.parse(FolderDeleteQueueMessage, json.loads(f_event_str))
            # Update log
            log.info(f'Received event {f_event}')
            
            folder_delete_revision_service.invoke_tcps_api(f_event)
    except Exception as e:
        log.error(f'Exception while processing the folder event {e}')
        # throw the exception so that lambda understands that the message is not processed successfully
        raise e 
    

