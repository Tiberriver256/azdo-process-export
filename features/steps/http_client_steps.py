"""
Behave step definitions for HTTP client testing.
Tests the async HTTP client functionality for Azure DevOps API calls.
"""

import asyncio
from pathlib import Path

from behave import given, then, when


@given("I have Azure DevOps connection details")
def step_have_azdo_connection_details(context):
    """Set up Azure DevOps connection details for testing."""
    # Use test values or environment variables
    context.azdo_organization = getattr(context, "test_organization", "demo-org")
    context.azdo_base_url = f"https://dev.azure.com/{context.azdo_organization}"
    context.azdo_pat = getattr(context, "test_pat", "dummy-pat-for-testing")


@given("I have a minimal HTTP client")
def step_have_minimal_http_client(context):
    """Initialize the minimal HTTP client."""
    try:
        # Try to import the HTTP client - this should fail initially (RED phase)
        from azdo_process_export.infrastructure.http_client import AzureDevOpsClient
        
        context.http_client = AzureDevOpsClient(
            organization=context.azdo_organization,
            pat=context.azdo_pat
        )
        context.client_imported = True
    except ImportError:
        context.client_imported = False
        context.import_error = "HTTP client module not found"


@when("I make an async request to list projects")
def step_make_async_request_list_projects(context):
    """Make an async request to list projects."""
    if not context.client_imported:
        context.api_error = context.import_error
        return
    
    try:
        # Run the async call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            context.api_response = loop.run_until_complete(
                context.http_client.list_projects()
            )
            context.api_error = None
        finally:
            loop.close()
    except Exception as e:
        context.api_error = str(e)
        context.api_response = None


@then("I should receive a successful response")
def step_should_receive_successful_response(context):
    """Verify the response was successful."""
    if context.api_error:
        raise AssertionError(f"API call failed: {context.api_error}")
    
    assert context.api_response is not None, "No response received"


@then("the response should contain project data")
def step_response_should_contain_project_data(context):
    """Verify the response contains project data."""
    if context.api_error:
        raise AssertionError(f"API call failed: {context.api_error}")
    
    # Verify response structure matches Azure DevOps Projects API format
    assert context.api_response is not None, "Response should not be None"
    assert isinstance(context.api_response, list), "Response should be a list of projects"
    
    # If we have projects, verify they have expected fields
    if context.api_response:
        project = context.api_response[0]
        assert isinstance(project, dict), "Each project should be a dictionary"
        
        # Azure DevOps Projects API returns projects with these core fields
        expected_fields = ["id", "name"]
        for field in expected_fields:
            assert field in project, f"Project should have '{field}' field"
            assert project[field] is not None, f"Project '{field}' should not be None"
        
        # Optional fields that are commonly present
        optional_fields = ["description", "url", "state", "revision", "visibility"]
        for field in optional_fields:
            if field in project:
                # Field exists, just verify it's not an empty string if present
                if isinstance(project[field], str):
                    # Allow empty strings, just check it's a string type
                    pass
