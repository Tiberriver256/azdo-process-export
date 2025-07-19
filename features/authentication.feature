Feature: Authentication Methods
    As a user of azdo-process-export
    I want to authenticate with Azure DevOps using different methods
    So that I can access my organization's data securely

    Background:
        Given I have access to the azdo-process-export CLI

    Scenario: Authenticate using Personal Access Token (PAT)
        Given I have a valid Personal Access Token
        And the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process 'Test Project' --pat 'valid-token'"
        Then the exit code should be 0
        And the structured log should contain authentication success with PAT credential source
        And the authentication headers should contain Basic authorization

    Scenario: Authenticate using DefaultAzureCredential when no PAT provided
        Given I have Azure AD credentials available
        And the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process 'Test Project'"
        Then the exit code should be 0
        And the structured log should contain authentication success with DefaultAzureCredential credential source
        And the authentication headers should contain Bearer authorization

    Scenario: Authentication fails with invalid PAT token
        Given I have an invalid Personal Access Token
        And the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process 'Test Project' --pat 'invalid-token'"
        Then the exit code should be 2
        And the structured log should contain authentication failure with PAT credential source
        And the error output should contain "Authentication failed"

    Scenario: Authentication fails when no Azure AD credentials available
        Given I have no Azure AD credentials available
        And the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process 'Test Project'"
        Then the exit code should be 2
        And the structured log should contain authentication failure with DefaultAzureCredential credential source
        And the error output should contain "Authentication failed"

    Scenario: Missing organization configuration causes failure
        Given I have a valid Personal Access Token
        When I run "azdo-process-export process 'Test Project' --pat 'valid-token'"
        Then the exit code should be 1
        And the error output should contain "Organization not specified"

    Scenario: Authentication success logging does not expose secrets
        Given I have a valid Personal Access Token
        And the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process 'Test Project' --pat 'secret-token-12345'"
        Then the exit code should be 0
        And the structured log should not contain "secret-token-12345"
        And the authentication headers should contain Basic authorization
