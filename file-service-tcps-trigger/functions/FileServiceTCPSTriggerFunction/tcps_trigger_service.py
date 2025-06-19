"""This module invokes the TCPS API based on the incoming event."""
import logging as log
import os
from typing import Dict

from tcps_common.auth.identity_auth import IdentityAuth
from model.file_event import FileOrFolderEvent, FileOrFolderData, FileFolderPermissionEventData
from tcps_common.utils import api_client
from tcps_common.utils.api_client import ApiError


class TCPSTriggerService(object):
    """A class with functions to invoke TCPS API making use of incoming event."""

    def __init__(self):
        self.__identity_auth = IdentityAuth()
        self.__tcps_base_url = os.environ['TCPS_BASE_URL']

    def invoke_tcps_api(self, file_folder_event: FileOrFolderEvent):
        """
        Performs TCPS API trigger for the file event.
        :param file_folder_event: file service event derived from sns message
        """
        permission_data = file_folder_event.file_permission_event_data or file_folder_event.file_folder_permission_event_data
        file_id = permission_data.file_id if permission_data else file_folder_event.object_data.id if file_folder_event.object_data else "Unknown"
        folder_id = permission_data.folder_id if permission_data else file_folder_event.object_data.id if file_folder_event.object_data else "Unknown"
        log.info(f'Performing TCPS API Trigger for the file {file_id}')
        log.info(f'Performing TCPS API Trigger for the folder {folder_id}')
        # Create request body
        request_body = TCPSTriggerService.prepare_request_body(file_folder_event)
        # Create request headers
        request_headers = self.__identity_auth.prepare_request_headers()
        # Prepare API Endpoint
        api_endpoint = self.__tcps_base_url + "/tc/api/2.0/files/processAsync"
        # Perform the TCPS API call
        try:
            api_client.ApiClient.make_request("POST", api_endpoint, request_headers, request_body)
        except ApiError as api_error:
            # clear the saved token and expiry if response code is 401
            if api_error.response_code == 401:
                self.__identity_auth.clear_access_token_and_expiry()
            raise api_error

    @staticmethod
    def prepare_request_body(file_folder_event: FileOrFolderEvent) -> Dict:
        """
        Preapare the request body for invoking the TCPS API based on the file event.
        :param file_folder_event: file event
        :return: request body as Dict.
        """
        if file_folder_event.file_permission_event_data:
            return TCPSTriggerService.prepare_permission_request_body(file_folder_event.file_permission_event_data, file_folder_event)
        if file_folder_event.file_folder_permission_event_data:
            return TCPSTriggerService.prepare_permission_request_body(file_folder_event.file_folder_permission_event_data, file_folder_event)

        file_or_folder_data: FileOrFolderData = file_folder_event.object_data
        request_body = {
            "id": file_or_folder_data.id,
            "versionId": file_or_folder_data.version_id,
            "projectId": file_or_folder_data.project_id,
            "parentId": file_or_folder_data.parent_id,
            "parentType": file_or_folder_data.parent_type,
            "activityType": file_folder_event.event_type,
            "activityId": file_or_folder_data.activity_id,
            "modifiedOn": str(file_folder_event.event_time.isoformat()),
            "modifiedBy": {
                "id": file_folder_event.user_identity.id,
                "tiduuid": file_folder_event.user_identity.tiduuid
            },
            "correlationId": file_folder_event.correlation_id,
            "clientName": file_or_folder_data.client_name,
            "processingPriority": file_or_folder_data.processing_priority,
            "oldParentId": file_or_folder_data.old_parent_id,
            "oldName": file_or_folder_data.old_name,
            "moveRenameActivityId": file_or_folder_data.move_rename_activity_id,
            "oldVersionId": file_or_folder_data.old_version_id
        }
        if file_folder_event.event_type in ["FILE_ADD", "FILE_UPDATE"]:
            request_body["tcfsSpaceId"] = file_or_folder_data.tcfs_space_id
            request_body["tcfsFileId"] = file_or_folder_data.tcfs_file_id
            request_body["tcfsVersionId"] = file_or_folder_data.tcfs_version_id

        return request_body

    @staticmethod
    def prepare_permission_request_body(permission_data: FileFolderPermissionEventData, file_folder_event: FileOrFolderEvent) -> Dict:
        """
        Prepare the request body for FILE_PERMISSION_CHANGE events.
        :param permission_data: permission event data
        :param file_folder_event: file event
        :return: request body as Dict.
        """
        request_body = {
            "id": permission_data.file_id or permission_data.folder_id or "Unknown",
            "projectId": permission_data.project_id,
            "activityType": file_folder_event.event_type,
            "modifiedOn": str(file_folder_event.event_time.isoformat()),
            "modifiedBy": {
                "id": file_folder_event.user_identity.id,
                "tiduuid": file_folder_event.user_identity.tiduuid
            },
            "correlationId": file_folder_event.correlation_id,
            "newlyAddedPermissions": permission_data.newly_added_permissions,
            "updatedPermissions": permission_data.updated_permissions,
            "removedPermissions": permission_data.removed_permissions,
        }
        return request_body