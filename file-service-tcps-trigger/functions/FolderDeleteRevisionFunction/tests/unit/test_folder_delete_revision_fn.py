import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tcps_common.auth import tid_config_util
from tests.unit import test_data
from tests.unit.test_data import LambdaContext
from tcps_common.utils.api_client import ApiError


def test_handler(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    mocker.patch("utils.logging_utils.update_logger_format")
    
    import folder_delete_revision_fn
    mocker.patch.object(folder_delete_revision_fn.FolderDeleteRevisionService, "invoke_tcps_api")
    
    event_time = datetime.now()
    input_event = test_data.get_sqs_fifo_msg(event_time, is_folder_event=True)
    request_id = str(uuid.uuid4())
    
    folder_delete_revision_fn.handler(input_event, LambdaContext(request_id))
    
    # Verify the service was called once with the parsed event
    folder_delete_revision_fn.FolderDeleteRevisionService.invoke_tcps_api.assert_called_once()
    
    # Verify the call arguments match expected values
    call_args = folder_delete_revision_fn.FolderDeleteRevisionService.invoke_tcps_api.call_args[0][0]
    expected_event = test_data.get_folder_delete_event(event_time)
    assert call_args.created_by.id == expected_event.created_by.id
    assert call_args.input.folder_id == expected_event.input.folder_id
    assert call_args.input.activity_id == expected_event.input.activity_id
    assert call_args.result.download_url == expected_event.result.download_url


def test_handler_throws_exception(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    mocker.patch("utils.logging_utils.update_logger_format")
    
    import folder_delete_revision_fn
    mock_obj = mocker.patch.object(folder_delete_revision_fn.FolderDeleteRevisionService, "invoke_tcps_api")
    mock_obj.side_effect = raise_error
    
    input_event = test_data.get_sqs_fifo_msg(is_folder_event=True)
    with pytest.raises(ApiError) as api_error:
        folder_delete_revision_fn.handler(input_event, LambdaContext(str(uuid.uuid4())))
        assert api_error.__str__() == "Test API call failed"


def raise_error(arg1):
    raise ApiError(500, "Test API call failed") 