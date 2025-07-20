"""
Minimal async HTTP client for Azure DevOps API.

This module provides a simple HTTP client for making async requests to Azure DevOps APIs.
Follows Azure DevOps REST API patterns with proper authentication and error handling.
"""

import base64
from typing import Any, Dict, List
import structlog

import httpx


# Constants
DEFAULT_API_VERSION = "7.0"
BASE_URL_TEMPLATE = "https://dev.azure.com/{organization}"

logger = structlog.get_logger(__name__)


class AzureDevOpsClient:
    """
    Minimal async HTTP client for Azure DevOps API.
    
    Provides basic operations for interacting with Azure DevOps REST APIs
    using Personal Access Token authentication.
    
    Example:
        >>> client = AzureDevOpsClient("my-org", "my-pat")
        >>> projects = await client.list_projects()
        >>> print(f"Found {len(projects)} projects")
    """

    def __init__(self, organization: str, pat: str, api_version: str = DEFAULT_API_VERSION):
        """
        Initialize the Azure DevOps client.
        
        Args:
            organization: Azure DevOps organization name (e.g., 'my-company')
            pat: Personal Access Token for authentication
            api_version: Azure DevOps REST API version (default: '7.0')
            
        Raises:
            ValueError: If organization or PAT is empty or None
        """
        if not organization or not organization.strip():
            raise ValueError("Organization cannot be empty or None")
        if not pat or not pat.strip():
            raise ValueError("Personal Access Token cannot be empty or None")
            
        self.organization = organization.strip()
        self.api_version = api_version
        self.base_url = BASE_URL_TEMPLATE.format(organization=self.organization)
        self.headers = self._create_auth_headers(pat)
        
        logger.info(
            "Azure DevOps client initialized",
            organization=self.organization,
            base_url=self.base_url,
            api_version=self.api_version
        )

    def _create_auth_headers(self, pat: str) -> Dict[str, str]:
        """
        Create authentication headers for Azure DevOps API requests.
        
        Azure DevOps expects Basic authentication with PAT as username
        and empty password, base64 encoded.
        
        Args:
            pat: Personal Access Token
            
        Returns:
            Dictionary of HTTP headers for authentication
        """
        # Azure DevOps PAT format: ':PAT' (empty username, PAT as password)
        auth_string = f":{pat.strip()}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        return {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "azdo-process-export/0.1.0"
        }

    async def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects in the Azure DevOps organization.
        
        Makes an async GET request to /_apis/projects endpoint to retrieve
        all projects accessible to the authenticated user.
        
        Returns:
            List of project dictionaries containing project metadata.
            Each project dict includes: id, name, description, url, state, etc.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails (4xx/5xx status)
            httpx.RequestError: If there's a network or connection error
            ValueError: If the response format is unexpected
            
        Example:
            >>> projects = await client.list_projects()
            >>> for project in projects:
            ...     print(f"Project: {project['name']} (ID: {project['id']})")
        """
        url = f"{self.base_url}/_apis/projects"
        params = {"api-version": self.api_version}
        
        logger.debug(
            "Making request to list projects",
            url=url,
            params=params
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                projects = data.get("value", [])
                
                logger.info(
                    "Successfully retrieved projects",
                    project_count=len(projects),
                    status_code=response.status_code
                )
                
                return projects
                
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error while listing projects",
                status_code=e.response.status_code,
                response_text=e.response.text,
                url=url
            )
            raise
        except httpx.RequestError as e:
            logger.error(
                "Network error while listing projects",
                error=str(e),
                url=url
            )
            raise
        except (KeyError, TypeError, ValueError) as e:
            logger.error(
                "Invalid response format while listing projects",
                error=str(e),
                url=url
            )
            raise ValueError(f"Unexpected response format from Azure DevOps API: {e}")
