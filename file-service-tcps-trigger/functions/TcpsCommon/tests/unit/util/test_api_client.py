import pytest
from pytest_mock import MockerFixture
from requests import Response

from tcps_common.utils import api_client
from tcps_common.utils.api_client import ApiError


def test_make_request_raises_exception(mocker: MockerFixture):

    expected_response = Response()
    expected_response.status_code = 400
    request_mock = mocker.patch.object(api_client.requests, "request")
    request_mock.return_value = expected_response

    with pytest.raises(ApiError) as api_error:
        api_client.ApiClient().make_request("POST", "https://dummy-endpoint", {}, {})
    assert api_error.value.response_code == 400
    assert api_error.value.message == "API call failed with response code: 400"


def test_make_request_reties_exception(mocker: MockerFixture):
    expected_response = Response()
    expected_response.status_code = 500
    request_mock = mocker.patch.object(api_client.requests, "request")
    request_mock.return_value = expected_response

    with pytest.raises(ApiError) as api_error:
        api_client.ApiClient().make_request("POST", "https://dummy-endpoint", {}, {})
    assert api_error.value.response_code == 500
    assert request_mock.call_count == 3 