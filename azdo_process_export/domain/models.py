"""
Domain models for Azure DevOps process export.

Core data structures representing the business domain of Azure DevOps projects,
independent of infrastructure concerns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


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
class Project:
    """Azure DevOps project information."""
    id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    state: Optional[str] = None
    revision: Optional[int] = None
    visibility: Optional[str] = None


@dataclass
class WorkItemType:
    """Work item type definition."""
    name: str
    ref_name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_disabled: bool = False
    usage_last_12m: int = 0


@dataclass
class WorkItemField:
    """Work item field definition."""
    ref_name: str
    name: str
    type: str
    description: Optional[str] = None
    usage: Optional[str] = None
    read_only: bool = False
    can_sort_by: bool = True
    is_queryable: bool = True
    supported_operations: List[str] = field(default_factory=list)


@dataclass
class ProcessBehavior:
    """Process behavior configuration."""
    name: str
    ref_name: str
    inherits: Optional[str] = None
    description: Optional[str] = None
    abstract: bool = False


@dataclass
class TeamMember:
    """Team member information."""
    id: str
    display_name: str
    unique_name: str
    url: Optional[str] = None
    image_url: Optional[str] = None
    # Microsoft Graph enrichment
    aad_id: Optional[str] = None
    job_title: Optional[str] = None
    mail: Optional[str] = None
    role_hint: Optional[str] = None  # "PR-heavy", "work-item-heavy", etc.


@dataclass
class TeamSettings:
    """Team configuration settings."""
    working_days: List[str] = field(default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday"])
    bugs_behavior: BugBehavior = BugBehavior.AS_REQUIREMENTS
    default_iteration: Optional[str] = None
    default_iteration_macro: Optional[str] = None
    backlog_iteration: Optional[str] = None


@dataclass
class Team:
    """Azure DevOps team."""
    id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    project_id: Optional[str] = None
    settings: Optional[TeamSettings] = None
    members: List[TeamMember] = field(default_factory=list)


@dataclass
class BacklogLevel:
    """Backlog level configuration."""
    id: str
    name: str
    ref_name: str
    rank: int
    color: Optional[str] = None
    work_item_types: List[str] = field(default_factory=list)


@dataclass
class Metrics:
    """Activity metrics aggregated by month."""
    work_items_created_per_month: Dict[str, int] = field(default_factory=dict)
    work_items_closed_per_month: Dict[str, int] = field(default_factory=dict)
    work_items_updated_per_month: Dict[str, int] = field(default_factory=dict)
    prs_created_per_month: Dict[str, int] = field(default_factory=dict)
    prs_merged_per_month: Dict[str, int] = field(default_factory=dict)
    pipeline_runs_per_month: Dict[str, int] = field(default_factory=dict)


@dataclass
class ProcessExport:
    """Complete process export data model."""
    exported_at: datetime
    project: Project
    work_item_types: List[WorkItemType] = field(default_factory=list)
    fields: List[WorkItemField] = field(default_factory=list)
    behaviors: List[ProcessBehavior] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)
    backlog_levels: List[BacklogLevel] = field(default_factory=list)
    metrics: Optional[Metrics] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
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
                    } if team.settings else None,
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
            } if self.metrics else None,
            "warnings": self.warnings,
        }