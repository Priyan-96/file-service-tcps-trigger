"""This module consist of functions to fetch app identity credentials from AWS SSM parameter store."""
import json
import logging as log
import os
from types import SimpleNamespace

import boto3


def get_tid_credentials() -> SimpleNamespace:
    """
    This function fetched the app identity credentials from aws parameter store
    @return: tid_credentials: SimpleNamespace
    """

    log.info("Fetching TID credentials from parameter store")
    # call parameter store service and fetch the value for the parameter
    response = boto3.client('ssm').get_parameter(
        Name=os.environ['TID_CREDENTIALS_PARAMETER'],
        WithDecryption=True
    )
    # Fetch the decrypted parameter value from the response
    decrypted: str = response['Parameter']['Value']
    log.info("Fetched the credentials from parameter store")
    # the decrypted parameter value is in string, hence converting it to typed object
    return json.loads(decrypted, object_hook=lambda d: SimpleNamespace(**d))
