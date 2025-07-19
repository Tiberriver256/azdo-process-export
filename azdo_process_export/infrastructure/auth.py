import base64
import logging
import os
import json
from typing import Tuple

logger = logging.getLogger("azdo_auth")

# Azure DevOps API scope constant
AZURE_DEVOPS_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"

class AuthenticationError(Exception):
    pass

def _emit_test_json_log(event_data: dict) -> None:
    """Emit JSON log for Behave tests if environment variable is set."""
    if os.environ.get("BEHAVE_JSON_LOGGING") == "1":
        print(json.dumps(event_data))

def _log_auth_success(credential_source: str, headers: dict) -> None:
    """Log successful authentication with both structured and test logging."""
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

def _log_auth_failure(credential_source: str, error: Exception, message: str) -> None:
    """Log authentication failure with structured logging."""
    logger.error(
        message,
        extra={
            "event": "auth_failure",
            "error": str(error),
            "credential_source": credential_source,
            "exception": repr(error)
        }
    )

def _authenticate_with_pat(pat: str) -> Tuple[dict, str]:
    """Authenticate using Personal Access Token."""
    try:
        basic = base64.b64encode(f":{pat}".encode()).decode()
        headers = {"Authorization": f"Basic {basic}"}
        credential_source = "PAT"
        
        _log_auth_success(credential_source, headers)
        return headers, credential_source
        
    except Exception as e:
        _log_auth_failure("PAT", e, "PAT authentication failed")
        raise AuthenticationError("PAT authentication failed") from e

def _authenticate_with_azure_ad() -> Tuple[dict, str]:
    """Authenticate using DefaultAzureCredential."""
    try:
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        token = credential.get_token(AZURE_DEVOPS_SCOPE)
        headers = {"Authorization": f"Bearer {token.token}"}
        credential_source = "DefaultAzureCredential"
        
        _log_auth_success(credential_source, headers)
        return headers, credential_source
        
    except Exception as e:
        _log_auth_failure("DefaultAzureCredential", e, "Azure AD authentication failed")
        raise AuthenticationError("Azure AD authentication failed") from e

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
        return _authenticate_with_pat(pat)
    else:
        return _authenticate_with_azure_ad()

# Backwards compatibility - deprecated
def get_auth_headers(pat: str = None) -> dict:
    """Deprecated: Use get_credentials() instead."""
    headers, _ = get_credentials(pat)
    return headers
