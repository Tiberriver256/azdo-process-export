"""
Project metadata service for Azure DevOps.

This module provides functionality to fetch project metadata from Azure DevOps
using the REST APIs.
"""

from typing import Optional

from azure.devops.connection import Connection
from azure.devops.v7_1.core.core_client import CoreClient
from azure.devops.v7_1.core.models import TeamProject
from msrest.authentication import BasicAuthentication
from azure.core.exceptions import ResourceNotFoundError
from msrest.exceptions import HttpOperationError

from azdo_process_export.domain.models import Project, Collection, Team


class ProjectNotFoundError(Exception):
    """Raised when a requested project cannot be found."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication with Azure DevOps fails."""
    pass


class ServiceUnavailableError(Exception):
    """Raised when the Azure DevOps service is unavailable."""
    pass


class ProjectMetadataService:
    """Service for fetching project metadata from Azure DevOps."""
    
    def __init__(self, organization_url: str, personal_access_token: str):
        """
        Initialize the ProjectMetadataService.
        
        Args:
            organization_url: The base URL of the Azure DevOps organization
            personal_access_token: Personal Access Token for authentication
        """
        self.organization_url = organization_url
        self.personal_access_token = personal_access_token
        
        # Initialize Azure DevOps connection
        credentials = BasicAuthentication('', personal_access_token)
        self._connection = Connection(base_url=organization_url, creds=credentials)
        self._core_client = self._connection.clients.get_core_client()
    
    def get_project_by_id(self, project_id: str) -> Project:
        """
        Fetch project metadata by project ID.
        
        Args:
            project_id: The ID of the project to fetch
            
        Returns:
            Project object with metadata
            
        Raises:
            ProjectNotFoundError: If the project doesn't exist
            AuthenticationError: If authentication fails
            ServiceUnavailableError: If the service is unavailable
        """
        try:
            # Fetch project data from Azure DevOps
            team_project = self._core_client.get_project(
                project_id=project_id,
                include_capabilities=True
            )
            
            # Convert Azure DevOps TeamProject to our domain model
            return self._convert_team_project_to_domain_model(team_project)
            
        except HttpOperationError as e:
            if e.response.status_code == 404:
                raise ProjectNotFoundError(f"Project with ID '{project_id}' not found")
            elif e.response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please check your credentials.")
            elif e.response.status_code >= 500:
                raise ServiceUnavailableError("Azure DevOps service is currently unavailable")
            else:
                raise ServiceUnavailableError(f"Azure DevOps API error: {e}")
        except Exception as e:
            # Check for Azure DevOps specific "project does not exist" error
            error_msg = str(e)
            if "TF200016" in error_msg or "does not exist" in error_msg:
                raise ProjectNotFoundError(f"Project with ID '{project_id}' not found")
            raise ServiceUnavailableError(f"Unexpected error: {e}")
    
    def list_projects(self, continuation_token: Optional[str] = None) -> list[Project]:
        """
        List all projects in the organization.
        
        Args:
            continuation_token: Token for pagination (optional)
            
        Returns:
            List of Project objects
            
        Raises:
            AuthenticationError: If authentication fails
            ServiceUnavailableError: If the service is unavailable
        """
        try:
            # Fetch projects data from Azure DevOps
            get_projects_response = self._core_client.get_projects(
                continuation_token=continuation_token
            )
            
            # Handle different response formats
            if hasattr(get_projects_response, 'value'):
                # Response has a .value attribute (wrapped response)
                project_list = get_projects_response.value
            else:
                # Response is the list directly
                project_list = get_projects_response
            
            # Convert Azure DevOps TeamProject objects to our domain models
            projects = []
            for team_project in project_list:
                project = self._convert_team_project_to_domain_model(team_project)
                projects.append(project)
            
            return projects
            
        except HttpOperationError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please check your credentials.")
            elif e.response.status_code >= 500:
                raise ServiceUnavailableError("Azure DevOps service is currently unavailable")
            else:
                raise ServiceUnavailableError(f"Azure DevOps API error: {e}")
        except Exception as e:
            raise ServiceUnavailableError(f"Unexpected error: {e}")
    
    def _convert_team_project_to_domain_model(self, team_project: TeamProject) -> Project:
        """
        Convert Azure DevOps TeamProject to our domain Project model.
        
        Args:
            team_project: Azure DevOps TeamProject object
            
        Returns:
            Project domain model object
        """
        # Create Collection object from the project data
        collection = Collection(
            id=getattr(team_project, 'collection_id', team_project.id),
            name=getattr(team_project, 'collection_name', 'DefaultCollection'),
            url=self.organization_url,
            collection_url=self.organization_url
        )
        
        # Create default Team object (Azure DevOps projects have a default team)
        default_team = Team(
            id=getattr(team_project, 'default_team_id', f"{team_project.id} Team"),
            name=getattr(team_project, 'default_team_name', f"{team_project.name} Team"),
            url=f"{team_project.url}/_apis/projects/{team_project.id}/teams/{team_project.id}%20Team"
        )
        
        return Project(
            id=team_project.id,
            name=team_project.name,
            description=getattr(team_project, 'description', ''),
            url=team_project.url,
            state=getattr(team_project, 'state', 'wellFormed'),
            revision=getattr(team_project, 'revision', 0),
            visibility=getattr(team_project, 'visibility', 'private'),
            collection=collection,
            default_team=default_team
        )
