import datetime
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from auth import identity_auth, tid_config_util
from tests.unit import test_data

expected_token = test_data.generate_random_string()


def test_prepare_request_headers(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()

    oauth_mock = mocker.patch.object(identity_auth.IdentityAuth, "get_app_access_token")
    oauth_mock.return_value = expected_token

    id_auth = identity_auth.IdentityAuth()
    headers = id_auth.prepare_request_headers()

    oauth_mock.assert_called_once()
    assert headers["Authorization"] == f"Bearer {expected_token}"
    assert headers["Content-Type"] == "application/json"


def test_get_app_access_token_new(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()

    expiry_at = datetime.datetime.now() + datetime.timedelta(hours=1)
    oauth_mock = mocker.patch.object(identity_auth.OAuth2Session, "fetch_token")
    oauth_mock.return_value = test_data.prepare_token_api_response(expected_token, expiry_at)

    id_auth = identity_auth.IdentityAuth()

    create_token_mock = mocker.spy(id_auth, "_IdentityAuth__create_app_access_token")
    token = id_auth.get_app_access_token()

    create_token_mock.assert_called_once()
    assert token == expected_token


def test_get_app_access_token_existing(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()

    expiry_at = datetime.datetime.now() + datetime.timedelta(hours=1)
    oauth_mock = mocker.patch.object(identity_auth.OAuth2Session, "fetch_token")
    oauth_mock.return_value = test_data.prepare_token_api_response(expected_token, expiry_at)

    id_auth = identity_auth.IdentityAuth()
    id_auth.get_app_access_token()

    create_token_mock = mocker.spy(id_auth, "_IdentityAuth__create_app_access_token")

    token = id_auth.get_app_access_token()

    assert token == expected_token
    create_token_mock.assert_not_called()


def test_get_app_access_token_existing_expired(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()

    expected_new_token = test_data.generate_random_string()
    expiry_at = datetime.datetime.now() + datetime.timedelta(hours=1)

    oauth_mock = mocker.patch.object(identity_auth.OAuth2Session, "fetch_token")
    oauth_mock.return_value = test_data.prepare_token_api_response(expected_new_token, expiry_at)
    id_auth = identity_auth.IdentityAuth()
    create_token_mock = mocker.spy(id_auth, "_IdentityAuth__create_app_access_token")

    token = id_auth.get_app_access_token()

    assert token == expected_new_token
    create_token_mock.assert_called_once()
