"""
Domain models for Azure DevOps process export.

Core data structures representing the business domain of Azure DevOps projects,
independent of infrastructure concerns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class BugBehavior(str, Enum):
    """Team bug behavior settings."""

    AS_REQUIREMENTS = "asRequirements"
    AS_TASKS = "asTasks"
    OFF = "off"


class WorkItemState(str, Enum):
    """Common work item states."""

    NEW = "New"
    ACTIVE = "Active"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    REMOVED = "Removed"


@dataclass
class Collection:
    """Azure DevOps project collection information."""

    id: str
    name: str
    url: str
    collection_url: str


@dataclass
class Project:
    """Azure DevOps project information."""

    id: str
    name: str
    description: str | None = None
    url: str | None = None
    state: str | None = None
    revision: int | None = None
    visibility: str | None = None
    collection: Collection | None = None
    default_team: "Team | None" = None


@dataclass
class WorkItemType:
    """Work item type definition."""

    name: str
    ref_name: str
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    is_disabled: bool = False
    usage_last_12m: int = 0


@dataclass
class WorkItemField:
    """Work item field definition."""

    ref_name: str
    name: str
    type: str
    description: str | None = None
    usage: str | None = None
    read_only: bool = False
    can_sort_by: bool = True
    is_queryable: bool = True
    supported_operations: list[str] = field(default_factory=list)


@dataclass
class ProcessBehavior:
    """Process behavior configuration."""

    name: str
    ref_name: str
    inherits: str | None = None
    description: str | None = None
    abstract: bool = False


@dataclass
class TeamMember:
    """Team member information."""

    id: str
    display_name: str
    unique_name: str
    url: str | None = None
    image_url: str | None = None
    # Microsoft Graph enrichment
    aad_id: str | None = None
    job_title: str | None = None
    mail: str | None = None
    role_hint: str | None = None  # "PR-heavy", "work-item-heavy", etc.


@dataclass
class TeamSettings:
    """Team configuration settings."""

    working_days: list[str] = field(default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday"])
    bugs_behavior: BugBehavior = BugBehavior.AS_REQUIREMENTS
    default_iteration: str | None = None
    default_iteration_macro: str | None = None
    backlog_iteration: str | None = None


@dataclass
class Team:
    """Azure DevOps team."""

    id: str
    name: str
    description: str | None = None
    url: str | None = None
    project_id: str | None = None
    settings: TeamSettings | None = None
    members: list[TeamMember] = field(default_factory=list)


@dataclass
class BacklogLevel:
    """Backlog level configuration."""

    id: str
    name: str
    ref_name: str
    rank: int
    color: str | None = None
    work_item_types: list[str] = field(default_factory=list)


@dataclass
class Metrics:
    """Activity metrics aggregated by month."""

    work_items_created_per_month: dict[str, int] = field(default_factory=dict)
    work_items_closed_per_month: dict[str, int] = field(default_factory=dict)
    work_items_updated_per_month: dict[str, int] = field(default_factory=dict)
    prs_created_per_month: dict[str, int] = field(default_factory=dict)
    prs_merged_per_month: dict[str, int] = field(default_factory=dict)
    pipeline_runs_per_month: dict[str, int] = field(default_factory=dict)


@dataclass
class ProcessExport:
    """Complete process export data model."""

    exported_at: datetime
    project: Project
    work_item_types: list[WorkItemType] = field(default_factory=list)
    fields: list[WorkItemField] = field(default_factory=list)
    behaviors: list[ProcessBehavior] = field(default_factory=list)
    teams: list[Team] = field(default_factory=list)
    backlog_levels: list[BacklogLevel] = field(default_factory=list)
    metrics: Metrics | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "exportedAt": self.exported_at.isoformat(),
            "project": {
                "id": self.project.id,
                "name": self.project.name,
                "description": self.project.description,
                "url": self.project.url,
                "state": self.project.state,
                "revision": self.project.revision,
                "visibility": self.project.visibility,
            },
            "workItemTypes": [
                {
                    "name": wit.name,
                    "refName": wit.ref_name,
                    "description": wit.description,
                    "color": wit.color,
                    "icon": wit.icon,
                    "isDisabled": wit.is_disabled,
                    "usageLast12M": wit.usage_last_12m,
                }
                for wit in self.work_item_types
            ],
            "fields": [
                {
                    "refName": field.ref_name,
                    "name": field.name,
                    "type": field.type,
                    "description": field.description,
                    "usage": field.usage,
                    "readOnly": field.read_only,
                    "canSortBy": field.can_sort_by,
                    "isQueryable": field.is_queryable,
                    "supportedOperations": field.supported_operations,
                }
                for field in self.fields
            ],
            "behaviors": [
                {
                    "name": behavior.name,
                    "refName": behavior.ref_name,
                    "inherits": behavior.inherits,
                    "description": behavior.description,
                    "abstract": behavior.abstract,
                }
                for behavior in self.behaviors
            ],
            "teams": [
                {
                    "id": team.id,
                    "name": team.name,
                    "description": team.description,
                    "url": team.url,
                    "projectId": team.project_id,
                    "settings": {
                        "workingDays": team.settings.working_days if team.settings else [],
                        "bugsBehavior": team.settings.bugs_behavior.value if team.settings else None,
                        "defaultIteration": team.settings.default_iteration if team.settings else None,
                        "defaultIterationMacro": team.settings.default_iteration_macro if team.settings else None,
                        "backlogIteration": team.settings.backlog_iteration if team.settings else None,
                    }
                    if team.settings
                    else None,
                    "members": [
                        {
                            "id": member.id,
                            "displayName": member.display_name,
                            "uniqueName": member.unique_name,
                            "url": member.url,
                            "imageUrl": member.image_url,
                            "aadId": member.aad_id,
                            "jobTitle": member.job_title,
                            "mail": member.mail,
                            "roleHint": member.role_hint,
                        }
                        for member in team.members
                    ],
                }
                for team in self.teams
            ],
            "backlogLevels": [
                {
                    "id": level.id,
                    "name": level.name,
                    "refName": level.ref_name,
                    "rank": level.rank,
                    "color": level.color,
                    "workItemTypes": level.work_item_types,
                }
                for level in self.backlog_levels
            ],
            "metrics": {
                "workItemsCreatedPerMonth": self.metrics.work_items_created_per_month,
                "workItemsClosedPerMonth": self.metrics.work_items_closed_per_month,
                "workItemsUpdatedPerMonth": self.metrics.work_items_updated_per_month,
                "prsCreatedPerMonth": self.metrics.prs_created_per_month,
                "prsMergedPerMonth": self.metrics.prs_merged_per_month,
                "pipelineRunsPerMonth": self.metrics.pipeline_runs_per_month,
            }
            if self.metrics
            else None,
            "warnings": self.warnings,
        }
