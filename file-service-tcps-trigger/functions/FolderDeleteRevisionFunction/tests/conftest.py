"""
Pytest configuration file for the FolderDeleteRevisionFunction tests.
"""
import os

# Set environment variables for testing
os.environ['TCPS_BASE_URL'] = "https://app.int.connect.trimble.com"
os.environ['AWS_REGION'] = "us-east-1"
os.environ['SSM_KEY_PARAM_NAME'] = "/tid/fileservice-tcps-trigger/key"
os.environ['TID_CREDENTIALS_PARAMETER'] = "/tid/test-credentials"