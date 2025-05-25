import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('AWS_EMF_ENVIRONMENT', 'Local')
    monkeypatch.setenv('TC_ENVIRONMENT', 'Test')
    monkeypatch.setenv('TID_CREDENTIALS_PARAMETER', 'testParameterName')
    monkeypatch.setenv('TCPS_BASE_URL', 'https://app.int.connect.trimble.com')
    monkeypatch.setenv('ECOM_BASE_URL', 'https://ecom.int.connect.trimble.com')
    monkeypatch.setenv('ECOM_REGION', 'na')