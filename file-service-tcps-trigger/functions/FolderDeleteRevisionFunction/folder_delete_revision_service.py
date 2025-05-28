"""This module invokes the Folder Delete Revision Log API based on the incoming event."""
import logging as log
import os
from typing import Dict

from auth.identity_auth import IdentityAuth
from model.folder_event import FolderDeleteQueueMessage
from utils import api_client
from utils.api_client import ApiError


class FolderDeleteRevisionService(object):
    """A class with functions to invoke Folder Delete Revision Log API making use of incoming event."""

    def __init__(self):
        self.__identity_auth = IdentityAuth()
        self.__tcps_base_url = os.environ['TCPS_BASE_URL']

    def invoke_tcps_api(self, folder_event: FolderDeleteQueueMessage):
        """
        Performs Folder Delete Revision for the folder event.
        :param folder_event: folder service event derived from sns message
        """
        folder_id = folder_event.input.folder_id if folder_event else "Unknown"
        # Create request body
        request_body = FolderDeleteRevisionService.prepare_request_body(folder_event)
        # Create request headers
        request_headers = self.__identity_auth.prepare_req
        # Prepare API Endpoint
        api_endpoint  self.__tcps_base_url + "/tc/api/2.0/files/logRevisionAsync"
        # Perform the TCPS API call
        try:
            api_client.ApiClient.make_request("POST", api_endpoint, request_headers, request_body)
        except ApiError as api_error:
            # clear the saved token and expiry if response code is 401
            if api_error.response_code == 401:
                self.__identity_auth.clear_access_token_and_expiry()
            raise api_error
        
    @staticmethod
    def prepare_request_body(folder_event: FolderDeleteQueueMessage) -> Dict:
        """
        Prepare the request body for Folder Delete Revision events.
        :param folder_event: folder event
        :return: request body as Dict.
        """
        request_body = {
            "userId": folder_event.input.user_id,
            "folderId": folder_event.input.f_id,
            "activityId": folder_event.input.a_id,
            "downloadUrl": folder_event.result.download_url
        }
        return request_body
