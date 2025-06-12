"""This module consists of functions that help in making http calls using request library."""
import requests
import logging as log
import backoff
from requests.models import Response

from utils import cloudwatch_util


# Custom Exception class for raising exceptions in ApiClient class
class ApiError(Exception):
    """Class that represents the exception thrown on API call error."""

    def __init__(self, response_code, error_code=None, message="API call failed"):
        self.response_code = response_code
        self.error_code = error_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ApiClient(object):
    """Performs http(s) calls and throws ApiError in case response code is not < 300."""

    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        ApiError,
        max_tries=3,
        max_time=60,  # Seconds
        giveup=lambda e: e.response_code < 500,
        logger=log
    )
    def make_request(method, endpoint, headers=None, data=None, *, url_pattern=None) -> Response:
        log.info(f'API ======== {method} {endpoint}')
        response: Response = requests.request(method, endpoint, headers=headers, json=data)
        latency = response.elapsed.total_seconds()
        log.info(f'Response Time ========= {latency}')
        response_code = response.status_code
        log.info(f'Response Status Code ======== [{response_code}]')
        if url_pattern is None:
            url_pattern = endpoint
        cloudwatch_util.log_embedded_metrics(f'{method} {url_pattern}', response_code, latency)
        # raise ApiError if response code is not less than 300
        if not response_code < 300:
            # logging response headers and body if api call fails
            log.error(f'Response Headers  ======== {response.headers}')
            
            # Enhanced logging for 403 errors - capture response body
            if response_code == 403:
                try:
                    response_body = response.text
                    log.error(f'Response Body (403 Forbidden) ======== {response_body}')
                except Exception as e:
                    log.error(f'Failed to read response body: {e}')
            
            error_code = ApiClient.parse_error_response(response)
            raise ApiError(response_code, error_code, "API call failed with response code: " + str(response_code))
        return response

    @staticmethod
    def parse_error_response(response):
        try:
            result = response.json()
            # Checking for two conventions of error code,
            # since monolith and microservices has different naming conventions.
            # Useful if such handling is required for monolith calls in future.
            if 'errorcode' in result:
                return result['errorcode']
            if 'errorCode' in result:
                return result['errorCode']
            return None
        except ValueError:
            return None
