# Azure DevOps Process Export – Product Requirements Document

## Executive Summary

The azdo-process-export initiative delivers a single-command Python CLI that captures every process-relevant facet of an Azure DevOps project into one comprehensive, portable JSON file. It enables delivery leads, process coaches, and analysts to obtain a point-in-time snapshot of configuration and activity trends—including work-item metadata, team settings, backlog hierarchy, pipelines, and usage metrics—without needing to stitch multiple APIs together.

The tool emphasises zero-configuration authentication inside Azure environments, graceful Personal Access Token (PAT) fallback, and a "Screaming Architecture" folder structure that separates domain logic from infrastructure details. Implementation is fully acceptance-test-driven (BDD with behave), and production readiness is ensured through structured logging, resilience to transient Azure DevOps outages, and ≤5-minute runtime on projects with up to 50k work items.

## Key Outcomes & Decisions

- **Scope**: One project per invocation; cross-org exports and data anonymisation are intentionally out-of-scope.
- **Primary Deliverable**: `azdo-process-export process --project "My Project" --out process.json` produces a ≤50 MB JSON artefact that feeds downstream HTML/Markdown report generators.
- **Authentication Strategy**: DefaultAzureCredential chain first; explicit --pat override accepted for non-Azure environments or Analytics scopes.
- **Performance**: Asyncio with up to 10 concurrent REST/OData requests; fatal exit if Analytics root is unreachable, but individual entity fetch failures downgrade to warnings.
- **Data Model**: Rich domain objects serialised by orjson include work-item types/fields, behaviours, teams, backlog levels, team settings, user enrichment, and monthly aggregates for work items, PRs, and pipeline runs.
- **Testing**: Pure BDD—each requirement mapped to Gherkin scenarios and executed against an ephemeral demo organisation during CI.
- **Observability**: JSON logs (Better Stack guidance), no root logger, trace-level available via --log-level trace.

## Open Questions

(to revisit in future sprint refinement)

1. Should export slicing (e.g., last N months only) be prioritised for very large projects?
2. Is Parquet or another columnar output needed sooner than later?
3. What is the minimal PAT scope we can request while still covering both REST and OData APIs?

## Goals

| Goal | Metric |
|------|--------|
| G1: Produce a single JSON file (< 50 MB in 95% of projects) capturing complete process configuration & activity trends for one project | File generated with exit code 0 |
| G2: Zero-configuration auth for developers running in any Azure environment | 90% of runs succeed with DefaultAzureCredential |
| G3: Enable downstream HTML/Markdown report generators | JSON schema published & versioned |
| G4: Runtime < 5 min on a project with ≤ 50k work items | 95th-percentile runtime measured in CI |

## Non-Goals

- Cross-project or cross-org exports
- Data anonymization or PII stripping
- Rendering reports – only raw collection here
- Real-time watching/streaming of project changes

## Personas & Use-Cases

- **Delivery Lead** – wants to understand backlog health before takeover.
- **Process Coach** – audits team settings to spot anti-patterns.
- **Data Analyst** – pipes the JSON into Power BI or Pandas to build visuals.

## Key Requirements

### Functional Requirements

#### 1. Export Metadata

- Work-item types (`GET /wit/workitemtypes`)
- Work-item fields (`GET /wit/fields`)
- Work-item behaviors per process (`GET /processes/{id}/behaviors`)
- Teams list (`GET /_apis/projects/{projectId}/teams`)
- Backlog levels & hierarchy (`GET /work/backlogs`)
- Team settings (working days, bug behavior, default iteration) (`GET /work/teamsettings`)

#### 2. Export Activity Metrics via OData Analytics v4

- Monthly closed / created work-items (query WorkItemsSnapshot aggregated by CompletedDate & CreatedDate)
- Monthly work-item updates (WorkItemRevisions)
- Monthly PRs merged (PullRequestEvents)
- Monthly pipeline runs (`GET /pipelines/{id}/runs`)

#### 3. Enrich Users

Lookup each unique Azure DevOps identity in Microsoft Graph `GET /users/{id}` to pull job title & mail; annotate usage patterns (PR-heavy vs work-item-heavy) from Analytics counts.

#### 4. Authentication

- Attempt DefaultAzureCredential() chain first
- Accept `--pat $TOKEN` to feed BasicAuth for both REST & OData

#### 5. CLI UX

Single verb:
```bash
azdo-process-export process --project "My Project" \
                           [--pat $AZDO_PAT] \
                           --out process.json
```

### Non-Functional Requirements

- **Resilience** – any 429/503 retries with exponential back-off; fatal if Analytics root (/_odata) unreachable.
- **Performance** – parallelize entity downloads with asyncio + ten concurrent requests.
- **Observability** – structured JSON logs following Better Stack guidance (levels, timestamps, no root logger)

## Data Model

```json
{
  "exportedAt": "2025-07-08T15:04:05Z",
  "project": { "id": "...", "name": "My Project" },
  "workItemTypes": [{ "name": "User Story", "usageLast12M": 1234 }],
  "fields": [{ "refName": "System.Title", "type": "string" }],
  "behaviors": [{ "name": "EpicsKanban", "inherits": "Kanban" }],
  "teams": [{
    "id": "...",
    "name": "Backend",
    "settings": { "bugsBehavior": "asTasks", "workingDays": ["mon", "tue", "wed", "thu", "fri"] },
    "members": [{ "aadId": "...", "displayName": "Alice", "roleHint": "PR-heavy" }]
  }],
  "metrics": {
    "workItemsClosedPerMonth": { "2025-06": 42 },
    "prsMergedPerMonth": { "2025-06": 18 }
  }
}
```

## Error Handling & Warnings

| Scenario | Behavior |
|----------|----------|
| Analytics endpoint 404 | Log error, abort export with exit code 2 and message "Analytics extension disabled for this project; enable it or pass --skip-metrics." |
| 401/403 | Explain credential precedence and suggest --pat. |
| Partial data fetch failure | Collect successes, emit warnings array in JSON, set exit code 1. |

## CLI Help

Auto-generated by Click:

```
Usage: azdo-process-export process [OPTIONS] PROJECT_NAME

  Export every process artifact and activity metric for PROJECT_NAME into a
  single JSON file.

Options:
  --out PATH           Output file (default: ./process.json)
  --pat TEXT           Personal Access Token (overrides DefaultAzureCredential)
  --log-level [info|debug|trace]
  --skip-metrics       Export configuration only, no Analytics queries
  --version            Show version and exit.
  --help               Show this message and exit.
```

## Testing Strategy

- **Behaviour-Driven**: every requirement captured as a Gherkin scenario (features/) then automated with Behave
- **E2E only** – spin up an ephemeral Azure DevOps demo organization during CI; extensive Rich logs surface failures quickly

## Reference APIs

| Artifact | Endpoint |
|----------|----------|
| Work-Item Types | `/wit/workitemtypes` |
| Fields | `/wit/fields` |
| Behaviors | `/processes/{id}/behaviors` |
| Teams | `/core/teams` |
| Backlogs | `/work/backlogs` |
| Team Settings | `/work/teamsettings` |
| Pipeline Runs | `/pipelines/{id}/runs` |
| OData Analytics | `/_odata/v4.0-preview/...` |
| Azure AD user | `GET /users/{id}` (Graph) |

## References

- [DefaultAzureCredential class – Azure Identity](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Azure-DevOps Python SDK – GitHub](https://github.com/Microsoft/azure-devops-python-api)
- [Logging best practices – Better Stack](https://betterstack.com/community/guides/logging/logging-best-practices/)