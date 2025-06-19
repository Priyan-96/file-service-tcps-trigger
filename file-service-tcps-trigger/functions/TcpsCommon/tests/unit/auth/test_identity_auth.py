import datetime
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from tcps_common.auth import identity_auth, tid_config_util
from tcps_common.tests.unit import test_data

expected_token = "test_token"


def test_get_app_access_token_new(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = {"Parameter": {"Value": '{"tid_v4_token_url": "https://identity-stg.webkit.org/as/token.oauth2", "tid_v4_consumer_key": "test_key", "tid_v4_consumer_secret": "test_secret", "tid_v4_application_name": "test_app"}'}}

    expiry_at = datetime.datetime.now() + datetime.timedelta(hours=1)
    oauth_mock = mocker.patch.object(identity_auth.OAuth2Session, "fetch_token")
    oauth_mock.return_value = {"access_token": expected_token, "expires_at": expiry_at.timestamp()}

    id_auth = identity_auth.IdentityAuth()

    create_token_mock = mocker.spy(id_auth, "_IdentityAuth__create_app_access_token")
    token = id_auth.get_app_access_token()

    create_token_mock.assert_called_once()
    assert token == expected_token


def test_get_app_access_token_existing(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = {"Parameter": {"Value": '{"tid_v4_token_url": "https://identity-stg.webkit.org/as/token.oauth2", "tid_v4_consumer_key": "test_key", "tid_v4_consumer_secret": "test_secret", "tid_v4_application_name": "test_app"}'}}

    expiry_at = datetime.datetime.now() + datetime.timedelta(hours=1)
    oauth_mock = mocker.patch.object(identity_auth.OAuth2Session, "fetch_token")
    oauth_mock.return_value = {"access_token": expected_token, "expires_at": expiry_at.timestamp()}

    id_auth = identity_auth.IdentityAuth()
    id_auth.get_app_access_token()

    create_token_mock = mocker.spy(id_auth, "_IdentityAuth__create_app_access_token")

    token = id_auth.get_app_access_token()

    assert token == expected_token
    create_token_mock.assert_not_called()


def test_get_app_access_token_existing_expired(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = {"Parameter": {"Value": '{"tid_v4_token_url": "https://identity-stg.webkit.org/as/token.oauth2", "tid_v4_consumer_key": "test_key", "tid_v4_consumer_secret": "test_secret", "tid_v4_application_name": "test_app"}'}}

    expected_new_token = "new_test_token"
    expiry_at = datetime.datetime.now() + datetime.timedelta(hours=1)

    oauth_mock = mocker.patch.object(identity_auth.OAuth2Session, "fetch_token")
    oauth_mock.return_value = {"access_token": expected_new_token, "expires_at": expiry_at.timestamp()}
    id_auth = identity_auth.IdentityAuth()
    create_token_mock = mocker.spy(id_auth, "_IdentityAuth__create_app_access_token")

    token = id_auth.get_app_access_token()

    assert token == expected_new_token
    create_token_mock.assert_called_once() 