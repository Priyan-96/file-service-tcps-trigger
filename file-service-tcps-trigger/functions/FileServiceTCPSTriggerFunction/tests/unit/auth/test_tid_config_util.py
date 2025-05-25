from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from auth import tid_config_util
from tests.unit import test_data


def test_get_db_credentials(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    response = tid_config_util.get_tid_credentials()
    expected = test_data.prepare_tid_config_json()
    assert response.tid_v4_token_url == expected['tid_v4_token_url']
    assert response.tid_v4_consumer_key == expected['tid_v4_consumer_key']
    assert response.tid_v4_consumer_secret == expected['tid_v4_consumer_secret']
    assert response.tid_v4_application_name == expected['tid_v4_application_name']
