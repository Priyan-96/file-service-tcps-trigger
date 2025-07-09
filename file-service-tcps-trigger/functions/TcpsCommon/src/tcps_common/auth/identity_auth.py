"""
This module consists of IdentityAuth class that has functions to help with fetching app access token from TID.
"""

import datetime
import logging as log
from typing import Dict

from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from tcps_common.auth import tid_config_util


class IdentityAuth(object):
    """A class with functions to perform operations related to TID tokens."""

    def __init__(self):
        self.__tid_credentials = tid_config_util.get_tid_credentials()
        self.__access_token = None
        self.__access_token_expiry = None

    def __create_app_access_token(self):
        """
        Performs create token api call to fetch the app access token and saves the token and expiry time in cache.
        """

        log.info("Performing create_app_access_token")
        auth = HTTPBasicAuth(self.__tid_credentials.tid_v4_consumer_key, self.__tid_credentials.tid_v4_consumer_secret)
        client = BackendApplicationClient(client_id=self.__tid_credentials.tid_v4_consumer_key,
                                          scope=[self.__tid_credentials.tid_v4_application_name])
        oauth = OAuth2Session(client=client)
        token_response = oauth.fetch_token(token_url=self.__tid_credentials.tid_v4_token_url, auth=auth)
        self.__access_token = token_response['access_token']
        self.__access_token_expiry = token_response['expires_at']
        log.info("create_app_access_token successful")

    def get_app_access_token(self) -> str:
        """
        Fetches the app access token. Returns from cache if token not expired.
        :return: accessToken
        """

        log.info("Performing get_app_access_token")
        if (self.__access_token is None) or \
                (self.__access_token is not None and
                 datetime.datetime.now().timestamp() > self.__access_token_expiry):
            log.info("Token expired or empty. Hence requesting new token")
            self.__create_app_access_token()
        return self.__access_token

    def prepare_request_headers(self) -> Dict:
        """
        Prepare the request headers to invoke the Connect API like Authorization header, UserAgent header.
        :return: request headers as Dict
        """
        return {
            "Authorization": "Bearer " + self.get_app_access_token(),
            "Content-Type": "application/json",
            "User-Agent": "TcpsTriggerService/1.0"
        }

    def clear_access_token_and_expiry(self):
        self.__access_token = None
        self.__access_token_expiry = None 