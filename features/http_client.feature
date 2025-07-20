Feature: Azure DevOps HTTP Client
  As a developer using the azdo-process-export tool
  I want to make HTTP requests to Azure DevOps APIs
  So that I can retrieve project information

  Background:
    Given I have Azure DevOps connection details
    And I have a minimal HTTP client

  Scenario: List projects from Azure DevOps API
    When I make an async request to list projects
    Then I should receive a successful response
    And the response should contain project data
