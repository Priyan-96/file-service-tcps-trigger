import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from auth import tid_config_util
from tests.unit import test_data
from tests.unit.test_data import LambdaContext
from utils.api_client import ApiError


def test_handler(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    import file_service_tcps_trigger_fn
    mocker.patch.object(file_service_tcps_trigger_fn.TCPSTriggerService, "invoke_tcps_api")
    mocker.patch.object(file_service_tcps_trigger_fn.EcomTriggerService, "update_ecom_transaction")
    event_time = datetime.now()
    input_event = test_data.get_sqs_fifo_msg(event_time)
    request_id = str(uuid.uuid4())
    file_service_tcps_trigger_fn.handler(input_event, LambdaContext(request_id))
    file_service_tcps_trigger_fn.EcomTriggerService.update_ecom_transaction \
        .assert_called_once_with(test_data.get_file_event(event_time))
    file_service_tcps_trigger_fn.TCPSTriggerService.invoke_tcps_api \
        .assert_called_once_with(test_data.get_file_event(event_time))


def test_handler_folder_event(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    import file_service_tcps_trigger_fn
    mocker.patch.object(file_service_tcps_trigger_fn.TCPSTriggerService, "invoke_tcps_api")
    mocker.patch.object(file_service_tcps_trigger_fn.EcomTriggerService, "update_ecom_transaction")
    event_time = datetime.now()
    input_event = test_data.get_sqs_fifo_msg(event_time,True)
    request_id = str(uuid.uuid4())
    file_service_tcps_trigger_fn.handler(input_event, LambdaContext(request_id))
    file_service_tcps_trigger_fn.EcomTriggerService.update_ecom_transaction \
        .assert_not_called()
    file_service_tcps_trigger_fn.TCPSTriggerService.invoke_tcps_api \
        .assert_called_once_with(test_data.get_folder_event(event_time))

def test_handler_file_permission_event(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()

    import file_service_tcps_trigger_fn
    mocker.patch.object(file_service_tcps_trigger_fn.TCPSTriggerService, "invoke_tcps_api")
    mocker.patch.object(file_service_tcps_trigger_fn.EcomTriggerService, "update_ecom_transaction")
    event_time = datetime.now()
    input_event = test_data.get_sqs_fifo_msg(event_time, is_file_permission_event = True)  # New method for file permission events
    request_id = str(uuid.uuid4())
    file_service_tcps_trigger_fn.handler(input_event, LambdaContext(request_id))
    # **Ensure Ecom Service is NOT called for file permission events**
    file_service_tcps_trigger_fn.EcomTriggerService.update_ecom_transaction.assert_not_called()
    # **Ensure TCPS API is called once**
    file_service_tcps_trigger_fn.TCPSTriggerService.invoke_tcps_api.assert_called_once_with(
        test_data.get_file_permission_event(event_time)
    )

def test_handler_folder_permission_event(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()

    import file_service_tcps_trigger_fn
    mocker.patch.object(file_service_tcps_trigger_fn.TCPSTriggerService, "invoke_tcps_api")
    mocker.patch.object(file_service_tcps_trigger_fn.EcomTriggerService, "update_ecom_transaction")
    event_time = datetime.now()
    input_event = test_data.get_sqs_fifo_msg(event_time, is_folder_permission_event = True)  # New method for folder permission events
    request_id = str(uuid.uuid4())
    file_service_tcps_trigger_fn.handler(input_event, LambdaContext(request_id))
    # **Ensure Ecom Service is NOT called for folder permission events**
    file_service_tcps_trigger_fn.EcomTriggerService.update_ecom_transaction.assert_not_called()
    # **Ensure TCPS API is called once**
    file_service_tcps_trigger_fn.TCPSTriggerService.invoke_tcps_api.assert_called_once_with(
        test_data.get_folder_permission_event(event_time)
    )    

def test_handler_throws_exception(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    import file_service_tcps_trigger_fn
    mocker.patch.object(file_service_tcps_trigger_fn.EcomTriggerService, "update_ecom_transaction")
    mock_obj = mocker.patch.object(file_service_tcps_trigger_fn.TCPSTriggerService, "invoke_tcps_api")
    mock_obj.side_effect = raise_error
    input_event = test_data.get_sqs_fifo_msg()
    with pytest.raises(ApiError) as api_error:
        file_service_tcps_trigger_fn.handler(input_event, LambdaContext(str(uuid.uuid4())))
        assert api_error.__str__() == "Test API call failed"


def test_handler_ecom_api_throws_exception(mocker: MockerFixture):
    mocker.patch.object(tid_config_util, "boto3")
    tid_config_util.boto3.return_value = MagicMock(name='boto_return', return_value=...)
    tid_config_util.boto3.client.return_value.get_parameter.return_value = test_data.prepare_ssm_response()
    import file_service_tcps_trigger_fn
    mock_obj = mocker.patch.object(file_service_tcps_trigger_fn.EcomTriggerService, "update_ecom_transaction")
    mock_obj.side_effect = raise_error
    input_event = test_data.get_sqs_fifo_msg()
    with pytest.raises(ApiError) as api_error:
        file_service_tcps_trigger_fn.handler(input_event, LambdaContext(str(uuid.uuid4())))
        assert api_error.__str__() == "Test API call failed"

def raise_error(arg1):
    raise ApiError(500, "Test API call failed")
