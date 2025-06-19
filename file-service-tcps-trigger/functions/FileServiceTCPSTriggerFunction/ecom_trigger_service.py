"""This module invokes the TCPS API based on the incoming event."""
import logging as log
import os

from tcps_common.auth.identity_auth import IdentityAuth
from model.file_event import FileOrFolderEvent, FileOrFolderData
from tcps_common.utils import api_client
from tcps_common.utils.api_client import ApiError


class EcomTriggerService(object):
    """A class with functions to invoke ECOM API making use of incoming event."""

    def __init__(self):
        self.__identity_auth = IdentityAuth()
        self.__ecom_base_url = os.environ['ECOM_BASE_URL']
        self.__ecom_region = os.environ['ECOM_REGION']

    def update_ecom_transaction(self, file_event: FileOrFolderEvent):
        """
        Perform ecom transaction update operation
        @param file_event: file service event derived from sns message
        """
        file_data: FileOrFolderData = file_event.object_data
        log.info(f'Performing ecom transaction update for the file {[file_data.id]}')
        # Prepare request body
        request_body = {
            "id": file_data.ecom_transaction_id,
            "entitlementId": file_data.entitlement_id,
            "projectId": file_data.project_id,
            "action": "FILE_ADD",
            "region": self.__ecom_region,
            "count": file_data.file_size,
            "status": "DONE",
            "createdBy": file_event.user_identity.tiduuid,
            "modifiedBy": file_event.user_identity.tiduuid,
        }
        log.info(f'ECOM Transaction Request Body {request_body}')
        # Prepare API Endpoint
        ecom_tx_api_url = self.__ecom_base_url + "/v1/transactions/"
        api_endpoint = ecom_tx_api_url + file_data.ecom_transaction_id
        # Perform the ECOM API call
        try:
            api_client.ApiClient.make_request("PUT", api_endpoint, self.__identity_auth.prepare_request_headers(),
                                              request_body, url_pattern=ecom_tx_api_url + '{id}')
        except ApiError as api_error:
            # clear the saved token and expiry if response code is 401
            if api_error.response_code == 401:
                self.__identity_auth.clear_access_token_and_expiry()

            # If ecom update transaction already done error occurs, skip it.
            if api_error.response_code == 400:
                if api_error.error_code is not None and api_error.error_code == 'TRANSACTION_ALREADY_COMPLETED':
                    log.debug("ECOM update transaction already completed, hence skipping it.")
                    return

            raise api_error
