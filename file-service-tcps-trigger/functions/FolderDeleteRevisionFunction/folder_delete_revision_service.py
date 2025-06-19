"""This module invokes the Folder Delete Revision Log API based on the incoming event."""
import logging as log
import os
from typing import Dict
from dataclasses import asdict
from tcps_common.auth.identity_auth import IdentityAuth
from model.folder_event import FolderDeleteQueueMessage
from tcps_common.utils import api_client
from tcps_common.utils.api_client import ApiError


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
        log.info(f'Performing Folder Delete Revision for the folder {folder_id}')
        # Create request body
        request_body = FolderDeleteRevisionService.prepare_request_body(folder_event)
        # Create request headers
        request_headers = self.__identity_auth.prepare_request_headers()
        # Prepare API Endpoint
        api_endpoint = self.__tcps_base_url + "/tc/api/2.0/folders/logRevisionAsync"
        
        # Perform the TCPS API call
        try:
            api_client.ApiClient.make_request("POST", api_endpoint, request_headers, request_body)
            log.info(f'Successfully invoked TCPS API for folder delete revision: {folder_id}')
        except ApiError as api_error:
            # Enhanced error logging for 403 errors
            if api_error.response_code == 401:
                self.__identity_auth.clear_access_token_and_expiry()
                log.error(f'401 Unauthorized error for folder {folder_id}. Clearing cached token.')
            
            log.error(f'Failed to invoke TCPS API for folder {folder_id}: {api_error.message}')
            raise api_error
        
    @staticmethod
    def prepare_request_body(folder_event: FolderDeleteQueueMessage) -> Dict:
        """
        Prepare the request body for Folder Delete Revision events.
        :param folder_event: folder event
        :return: request body as Dict.
        """
        def safe_asdict(obj):
            """Safely convert object to dict, handling both dataclass instances and dictionaries."""
            if obj is None:
                return None
            # If it's already a dict, return as-is
            if isinstance(obj, dict):
                return obj
            # If it's a dataclass instance, convert to dict
            try:
                return asdict(obj)
            except TypeError:
                # If asdict fails, assume it's already a dict-like object
                return obj

        request_body = {
            "userId": folder_event.created_by.id,
            "folderId": folder_event.input.folder_id,
            "activityId": folder_event.input.activity_id,
            "downloadUrl": folder_event.result.download_url if folder_event.result else None,
            "objectToDelete": safe_asdict(folder_event.result.object_to_delete) if folder_event.result else None,
            "objectDeleted": safe_asdict(folder_event.result.object_deleted) if folder_event.result else None,
            "type": folder_event.result.type if folder_event.result else None,
            "parentStorageObjectId": folder_event.result.parent_storage_object_id if folder_event.result else None
        }
        return request_body
