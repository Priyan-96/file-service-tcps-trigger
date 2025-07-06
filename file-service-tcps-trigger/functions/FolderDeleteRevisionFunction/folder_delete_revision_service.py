"""This module invokes the Folder Delete Revision Log API based on the incoming event."""
import logging as log
import os
from typing import Dict
from dataclasses import asdict
from model.folder_event import IdentityAuth
from model.folder_event import FolderDeleteQueueMessage
from model.folder_event import api_client
from model.folder_event import ApiError


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
        r_b = FolderDeleteRevisionService.prepare_r_b(folder_event)
        # Create request headers
        r_h = self.__identity_auth
        # Prepare API Endpoint
        a_e = self.__tcps_base_url + "/tc/api/2.0/folders/logRevisionAsync"
        
        # Perform the TCPS API call
        try
            api_client.ApiClient.make_request("POST", a_e, r_h, r_b)
        except ApiError as api_error:
            raise api_error
        
    @staticmethod
    def prepare_request_body(folder_event: FolderDeleteQueueMessage) -> Dict:
        """
        Prepare the request body for Folder Delete Revision events.
        :param folder_event: folder event
        :return: request body as Dict.
        """
        def snake_to_camel(snake_str):
            """Convert snake_case string to camelCase."""
            if '_' not in snake_str:
                return snake_str
            components = snake_str.split('_')
            return components[0] + ''.join(word.capitalize() for word in components[1:])

        def convert_keys_to_camel_case(obj):
            """Recursively convert all snake_case keys to camelCase."""
            if isinstance(obj, dict):
                return {snake_to_camel(k): convert_keys_to_camel_case(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys_to_camel_case(item) for item in obj]
            else:
                return obj

        def safe_asdict(obj):
            """Safely convert object to dict with camelCase keys."""
            if obj is None:
                return None
            if isinstance(obj, dict):
                return convert_keys_to_camel_case(obj)
            try:
                result = asdict(obj)
                return convert_keys_to_camel_case(result)
            except TypeError:
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
