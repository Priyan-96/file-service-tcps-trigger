import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tcps_common.auth import tid_config_util
from tests.unit import test_data
from tcps_common.utils.api_client import ApiError

tcps_base_url = "https://app.int.connect.trimble.com"


def test_invoke_tcps_api(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    
    import folder_delete_revision_service
    identity_auth_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth, "prepare_request_headers")
    identity_auth_mock.return_value = test_data.get_expected_request_headers(test_token)
    api_client_mock = mocker.patch.object(folder_delete_revision_service.api_client.ApiClient, "make_request")

    folder_event = test_data.get_folder_delete_event(datetime.datetime.now())
    folder_delete_revision_service.FolderDeleteRevisionService().invoke_tcps_api(folder_event)

    identity_auth_mock.assert_called_once()
    headers = test_data.get_expected_request_headers(test_token)
    request_body = test_data.get_expected_folder_delete_request_body(folder_event)
    api_client_mock.assert_called_once_with("POST", tcps_base_url + "/tc/api/2.0/folders/logRevisionAsync", headers,
                                          request_body)


def test_invoke_tcps_api_raises_api_error(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    
    import folder_delete_revision_service
    identity_auth_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth, "prepare_request_headers")
    identity_auth_mock.return_value = test_data.get_expected_request_headers(test_token)
    identity_auth_clear_token_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth,
                                                       "clear_access_token_and_expiry")
    api_client_mock = mocker.patch.object(folder_delete_revision_service.api_client.ApiClient, "make_request")
    api_client_mock.side_effect = raise_500_error

    folder_event = test_data.get_folder_delete_event(datetime.datetime.now())
    with pytest.raises(ApiError):
        folder_delete_revision_service.FolderDeleteRevisionService().invoke_tcps_api(folder_event)

    identity_auth_clear_token_mock.assert_not_called()


def test_invoke_tcps_api_clears_token_on_401(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    
    import folder_delete_revision_service
    identity_auth_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth, "prepare_request_headers")
    identity_auth_mock.return_value = test_data.get_expected_request_headers(test_token)
    identity_auth_clear_token_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth,
                                                       "clear_access_token_and_expiry")
    api_client_mock = mocker.patch.object(folder_delete_revision_service.api_client.ApiClient, "make_request")
    api_client_mock.side_effect = raise_401_error

    folder_event = test_data.get_folder_delete_event(datetime.datetime.now())
    with pytest.raises(ApiError):
        folder_delete_revision_service.FolderDeleteRevisionService().invoke_tcps_api(folder_event)

    identity_auth_clear_token_mock.assert_called_once()


def test_prepare_request_body():
    folder_event = test_data.get_folder_delete_event(datetime.datetime.now())
    
    import folder_delete_revision_service
    request_body = folder_delete_revision_service.FolderDeleteRevisionService.prepare_request_body(folder_event)
    
    assert request_body["userId"] == folder_event.created_by.id
    assert request_body["folderId"] == folder_event.input.folder_id
    assert request_body["activityId"] == folder_event.input.activity_id
    assert request_body["downloadUrl"] == folder_event.result.download_url


def test_invoke_tcps_api_nested_folder(mocker: MockerFixture):
    """Test invoke_tcps_api with nested folder event (contains downloadUrl)"""
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    
    import folder_delete_revision_service
    identity_auth_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth, "prepare_request_headers")
    identity_auth_mock.return_value = test_data.get_expected_request_headers(test_token)
    api_client_mock = mocker.patch.object(folder_delete_revision_service.api_client.ApiClient, "make_request")

    nested_folder_event = test_data.get_nested_folder_delete_event(datetime.datetime.now())
    folder_delete_revision_service.FolderDeleteRevisionService().invoke_tcps_api(nested_folder_event)

    identity_auth_mock.assert_called_once()
    headers = test_data.get_expected_request_headers(test_token)
    request_body = test_data.get_expected_nested_folder_delete_request_body(nested_folder_event)
    api_client_mock.assert_called_once_with("POST", tcps_base_url + "/tc/api/2.0/folders/logRevisionAsync", headers,
                                          request_body)


def test_invoke_tcps_api_empty_folder(mocker: MockerFixture):
    """Test invoke_tcps_api with empty folder event (contains object details)"""
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    
    import folder_delete_revision_service
    identity_auth_mock = mocker.patch.object(folder_delete_revision_service.IdentityAuth, "prepare_request_headers")
    identity_auth_mock.return_value = test_data.get_expected_request_headers(test_token)
    api_client_mock = mocker.patch.object(folder_delete_revision_service.api_client.ApiClient, "make_request")

    empty_folder_event = test_data.get_empty_folder_delete_event(datetime.datetime.now())
    folder_delete_revision_service.FolderDeleteRevisionService().invoke_tcps_api(empty_folder_event)

    identity_auth_mock.assert_called_once()
    headers = test_data.get_expected_request_headers(test_token)
    request_body = test_data.get_expected_empty_folder_delete_request_body(empty_folder_event)
    api_client_mock.assert_called_once_with("POST", tcps_base_url + "/tc/api/2.0/folders/logRevisionAsync", headers,
                                          request_body)


def test_prepare_request_body_nested_folder():
    """Test prepare_request_body for nested folder event (with downloadUrl)"""
    nested_folder_event = test_data.get_nested_folder_delete_event(datetime.datetime.now())
    
    import folder_delete_revision_service
    request_body = folder_delete_revision_service.FolderDeleteRevisionService.prepare_request_body(nested_folder_event)
    
    assert request_body["userId"] == nested_folder_event.created_by.id
    assert request_body["folderId"] == nested_folder_event.input.folder_id
    assert request_body["activityId"] == nested_folder_event.input.activity_id
    assert request_body["downloadUrl"] == nested_folder_event.result.download_url
    assert request_body["objectToDelete"] is None
    assert request_body["objectDeleted"] is None
    assert request_body["type"] is None
    assert request_body["parentStorageObjectId"] is None


def test_prepare_request_body_empty_folder():
    """Test prepare_request_body for empty folder event (with object details)"""
    empty_folder_event = test_data.get_empty_folder_delete_event(datetime.datetime.now())
    
    import folder_delete_revision_service
    request_body = folder_delete_revision_service.FolderDeleteRevisionService.prepare_request_body(empty_folder_event)
    
    assert request_body["userId"] == empty_folder_event.created_by.id
    assert request_body["folderId"] == empty_folder_event.input.folder_id
    assert request_body["activityId"] == empty_folder_event.input.activity_id
    assert request_body["downloadUrl"] is None
    assert request_body["objectToDelete"] is not None
    assert request_body["objectDeleted"] is not None
    assert request_body["type"] == "FOLDER"
    assert request_body["parentStorageObjectId"] == 281474977707004
    
    # Verify object details
    object_to_delete = request_body["objectToDelete"]
    assert object_to_delete["storage_object_id"] == 281474977720987
    assert object_to_delete["name"] == "12"
    assert object_to_delete["type"] == "FOLDER"
    assert object_to_delete["flag"] is None
    
    object_deleted = request_body["objectDeleted"]
    assert object_deleted["storage_object_id"] == 281474977720988
    assert object_deleted["name"] == "12"
    assert object_deleted["type"] == "FOLDER"
    assert object_deleted["flag"] == "DELETED"


def raise_401_error(arg1, arg2, arg3, arg4):
    raise ApiError(401, "Test API call failed")


def raise_500_error(arg1, arg2, arg3, arg4):
    raise ApiError(500, "Test API call failed") 