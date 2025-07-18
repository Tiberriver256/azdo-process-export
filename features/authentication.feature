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
