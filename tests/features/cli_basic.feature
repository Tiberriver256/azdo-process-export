Feature: Basic CLI Functionality
  As a user of azdo-process-export
  I want to use the command-line interface
  So that I can export Azure DevOps process data

  Background:
    Given I have access to the azdo-process-export CLI

  Scenario: Display help information
    When I run "azdo-process-export --help"
    Then the exit code should be 0
    And the output should contain "Azure DevOps process export tool"
    And the output should contain "process"

  Scenario: Display version information
    When I run "azdo-process-export --version"
    Then the exit code should be 0
    And the output should contain "0.1.0"

  Scenario: Display process command help
    When I run "azdo-process-export process --help"
    Then the exit code should be 0
    And the output should contain "Export every process artifact"
    And the output should contain "--out"
    And the output should contain "--pat"
    And the output should contain "--skip-metrics"

  Scenario: Require project name argument
    When I run "azdo-process-export process"
    Then the exit code should be 2
    And the output should contain "Missing argument"

  Scenario: Require organization configuration
    When I run "azdo-process-export process 'Test Project'"
    Then the exit code should be 1
    And the output should contain "Organization not specified"

  Scenario: Process command with minimal arguments
    Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
    When I run "azdo-process-export process 'Test Project'"
    Then the exit code should be 0
    And the output should contain "Starting export for project: Test Project"
    And the output should contain "Export logic not yet implemented"