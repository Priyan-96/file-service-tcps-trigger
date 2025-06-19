"""
This module consists of the lambda handler function.
The Lambda function handler is the method in your function code that processes events.
"""
import json
import logging as log
from typing import Dict

import pyckson

from ecom_trigger_service import EcomTriggerService
from model.file_event import FileOrFolderEvent
from tcps_trigger_service import TCPSTriggerService
from tcps_common.utils import logging_utils

# x-ray tracing configuration
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(('requests',))

tcps_trigger_service = TCPSTriggerService()
ecom_trigger_service = EcomTriggerService()


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
    # global try-catch-all so that any exception that arises is caught here and logged
    try:
        # Perform TCPS API Trigger on  each record sequentially
        for record in event['Records']:
            # Convert sns event string to dict
            sns_event: Dict = json.loads(record['body'])
            # Get file or folder event string from sns message
            file_folder_event_str: str = sns_event['Message']
            # Convert the file or folder event string to FileOrFolderEvent object
            file_folder_event: FileOrFolderEvent = pyckson.parse(FileOrFolderEvent, json.loads(file_folder_event_str))
            # Update logger formatting to include correlation_id
            logging_utils.update_logger_format(request_id=request_id, correlation_id=file_folder_event.correlation_id)
            log.info(f'Received event {file_folder_event}')
            # validate data before executing ecom call in case of any older events. this will be removed later.
            if file_folder_event.object_data and file_folder_event.object_data.ecom_transaction_id is not None:
                ecom_trigger_service.update_ecom_transaction(file_folder_event)
            tcps_trigger_service.invoke_tcps_api(file_folder_event)
    except Exception as e:
        log.error(f'Exception while processing the file or folder event {e}')
        # throw the exception so that lambda understands that the message is not processed successfully
        raise e
