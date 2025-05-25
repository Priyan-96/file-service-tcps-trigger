import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from auth import tid_config_util
from tests.unit import test_data
from utils.api_client import ApiError

ecom_base_url = "https://ecom.int.connect.trimble.com"


def test_update_ecom_transaction_api(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    import ecom_trigger_service
    identity_auth_mock = mocker.patch.object(ecom_trigger_service.IdentityAuth, "get_app_access_token")
    identity_auth_mock.return_value = test_token
    api_client_mock = mocker.patch.object(ecom_trigger_service.api_client.ApiClient, "make_request")

    modified = datetime.datetime.now()
    file_event = test_data.get_file_event(modified)
    ecom_trigger_service.EcomTriggerService().update_ecom_transaction(file_event)

    identity_auth_mock.assert_called_once()
    headers = test_data.get_expected_request_headers(test_token)
    request_body = test_data.get_expected_ecom_request_body(modified)
    api_client_mock.assert_called_once_with("PUT",
                                            ecom_base_url + "/v1/transactions/" + file_event.object_data.ecom_transaction_id,
                                            headers,
                                            request_body, url_pattern=ecom_base_url + '/v1/transactions/{id}')


def test_update_ecom_transaction_api_raises_api_error(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    import ecom_trigger_service
    identity_auth_mock = mocker.patch.object(ecom_trigger_service.IdentityAuth, "get_app_access_token")
    identity_auth_mock.return_value = test_token
    identity_auth_clear_token_mock = mocker.patch.object(ecom_trigger_service.IdentityAuth,
                                                         "clear_access_token_and_expiry")
    api_client_mock = mocker.patch.object(ecom_trigger_service.api_client.ApiClient, "make_request")
    api_client_mock.side_effect = raise_500_error

    file_event = test_data.get_file_event(datetime.datetime.now())
    with pytest.raises(ApiError):
        ecom_trigger_service.EcomTriggerService().update_ecom_transaction(file_event)

    identity_auth_clear_token_mock.assert_not_called()


def test_update_ecom_transaction_api_clears_token_on_401(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    test_token = test_data.generate_random_string()
    import ecom_trigger_service
    identity_auth_mock = mocker.patch.object(ecom_trigger_service.IdentityAuth, "get_app_access_token")
    identity_auth_mock.return_value = test_token
    identity_auth_clear_token_mock = mocker.patch.object(ecom_trigger_service.IdentityAuth,
                                                         "clear_access_token_and_expiry")
    api_client_mock = mocker.patch.object(ecom_trigger_service.api_client.ApiClient, "make_request")
    api_client_mock.side_effect = raise_401_error

    file_event = test_data.get_file_event(datetime.datetime.now())
    with pytest.raises(ApiError):
        ecom_trigger_service.EcomTriggerService().update_ecom_transaction(file_event)

    identity_auth_clear_token_mock.assert_called_once()


def raise_401_error(arg1, arg2, arg3, arg4, *, url_pattern):
    raise ApiError(401, "Test API call failed")


def raise_500_error(arg1, arg2, arg3, arg4, *, url_pattern):
    raise ApiError(500, "Test API call failed")
