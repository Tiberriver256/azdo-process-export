Feature: Structured JSON Logging
    As a user of azdo-process-export
    I want to have structured JSON logging with different log levels
    So that I can capture and analyze log data in a machine-readable format

    Background:
        Given I have access to the azdo-process-export CLI

    Scenario: Default info level logging produces JSON output
        Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process --pat=valid-token 'Test Project'"
        Then the exit code should be 0
        And the output should contain structured JSON logs
        And the JSON logs should contain "timestamp" field
        And the JSON logs should contain "level" field
        And the JSON logs should contain "logger" field
        And the JSON logs should contain "event" field

    Scenario: Debug level logging shows additional debug information
        Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export --log-level=debug process --pat=valid-token 'Test Project'"
        Then the exit code should be 0
        And the output should contain structured JSON logs

    Scenario: Trace level logging includes trace context
        Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export --log-level=trace process --pat=valid-token 'Test Project'"
        Then the exit code should be 0
        And the output should contain structured JSON logs
        And the JSON logs should contain trace context information

    Scenario: Log file output creates JSON file
        Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        And I have a temporary directory for logs
        When I run "azdo-process-export --log-file=/tmp/test-logging.log process --pat=valid-token 'Test Project'"
        Then the exit code should be 0
        And a log file should be created at "/tmp/test-logging.log"
        And the log file should contain valid JSON

    Scenario: Structured logs do not expose sensitive information
        Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export process --pat=test-token 'Test Project'"
        Then the exit code should be 0
        And the structured log should not contain "test-token"

    Scenario: Multiple log entries maintain JSON format
        Given the environment variable "AZDO_ORGANIZATION" is set to "test-org"
        When I run "azdo-process-export --log-level=debug process --pat=valid-token 'Test Project'"
        Then the exit code should be 0
        And each line of log output should be valid JSON
        And the JSON logs should contain sequential timestamps