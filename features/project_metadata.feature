Feature: Project Metadata Retrieval
    As a user of azdo-process-export
    I want to fetch basic project metadata from Azure DevOps
    So that I can access project information programmatically

    Background:
        Given I have access to the project metadata service
        And I have a valid Azure DevOps organization URL
        And I have valid authentication credentials

    Scenario: Fetch project details by ID
        Given a test project exists in the organization
        When I fetch project metadata for the test project
        Then the project metadata should be returned
        And the project should have the expected ID
        And the project should have a name
        And the project should have a URL
        And the project collection information should be included
        And the project default team information should be included

    Scenario: Handle project not found
        Given a non-existent project ID is used
        When I fetch project metadata for the non-existent project
        Then a ProjectNotFoundError should be raised

    Scenario: List all projects in organization
        Given the organization has multiple projects
        When I list all projects in the organization
        Then a list of projects should be returned
        And each project should have basic metadata fields
        And the list should support pagination if needed
