import base64
import logging

logger = logging.getLogger("azdo_auth")

class AuthenticationError(Exception):
    pass

def get_auth_headers(pat: str = None) -> dict:
    """
    Returns authentication headers for Azure DevOps and OData APIs.
    If PAT is provided, uses Basic Auth. Otherwise, raises AuthenticationError (Azure AD fallback handled elsewhere).
    """
    if pat:
        try:
            basic = base64.b64encode(f":{pat}".encode()).decode()
            logger.info(
                "Authentication success",
                extra={
                    "event": "auth_success",
                    "credential_source": "PAT"
                }
            )
            return {"Authorization": f"Basic {basic}"}
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
            logger.info(
                "Authentication success",
                extra={
                    "event": "auth_success",
                    "credential_source": "DefaultAzureCredential"
                }
            )
            return {"Authorization": f"Bearer {token.token}"}
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
