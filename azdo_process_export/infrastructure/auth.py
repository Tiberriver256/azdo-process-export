import base64
import logging
import os
import json
from typing import Tuple

logger = logging.getLogger("azdo_auth")

class AuthenticationError(Exception):
    pass

def _emit_test_json_log(event_data: dict) -> None:
    """Emit JSON log for Behave tests if environment variable is set."""
    if os.environ.get("BEHAVE_JSON_LOGGING") == "1":
        print(json.dumps(event_data))

def get_credentials(pat: str = None) -> Tuple[dict, str]:
    """
    Returns authentication headers and credential source for Azure DevOps and OData APIs.
    
    Args:
        pat: Personal Access Token. If provided, uses Basic Auth. 
             If None, uses DefaultAzureCredential for Bearer token.
    
    Returns:
        Tuple of (auth_headers, credential_source)
        
    Raises:
        AuthenticationError: If authentication fails
    """
    if pat:
        try:
            basic = base64.b64encode(f":{pat}".encode()).decode()
            headers = {"Authorization": f"Basic {basic}"}
            credential_source = "PAT"
            
            # Structured logging
            logger.info(
                "Authentication success",
                extra={
                    "event": "auth_success",
                    "credential_source": credential_source
                }
            )
            
            # Test-specific JSON logging
            _emit_test_json_log({
                "event": "authentication_success",
                "credential_source": credential_source
            })
            _emit_test_json_log(headers)
            
            return headers, credential_source
            
        except Exception as e:
            logger.error(
                "PAT authentication failed",
                extra={
                    "event": "auth_failure",
                    "error": str(e),
                    "credential_source": "PAT",
                    "exception": repr(e)
                }
            )
            raise AuthenticationError("PAT authentication failed")
    else:
        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            scope = "499b84ac-1321-427f-aa17-267ca6975798/.default"
            token = credential.get_token(scope)
            headers = {"Authorization": f"Bearer {token.token}"}
            credential_source = "DefaultAzureCredential"
            
            # Structured logging
            logger.info(
                "Authentication success",
                extra={
                    "event": "auth_success",
                    "credential_source": credential_source
                }
            )
            
            # Test-specific JSON logging
            _emit_test_json_log({
                "event": "authentication_success",
                "credential_source": credential_source
            })
            _emit_test_json_log(headers)
            
            return headers, credential_source
            
        except Exception as e:
            logger.error(
                "Azure AD authentication failed",
                extra={
                    "event": "auth_failure",
                    "error": str(e),
                    "credential_source": "DefaultAzureCredential",
                    "exception": repr(e)
                }
            )
            raise AuthenticationError("Azure AD authentication failed")

# Backwards compatibility - deprecated
def get_auth_headers(pat: str = None) -> dict:
    """Deprecated: Use get_credentials() instead."""
    headers, _ = get_credentials(pat)
    return headers
