"""Application Tracker Pydantic models"""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from .jd import ConfidenceLabel


class PriorityLevel(str, Enum):
    """Focus guidance levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ARCHIVE = "archive"


class UrgencyLevel(str, Enum):
    """Action urgency levels"""
    IMMEDIATE = "immediate"
    SOON = "soon"
    ROUTINE = "routine"
    NONE = "none"


class PipelineStatus(str, Enum):
    """Pipeline health status"""
    HEALTHY = "healthy"
    THIN = "thin"
    OVERLOADED = "overloaded"
    STALLED = "stalled"


class PipelineTone(str, Enum):
    """Pipeline recommendation tone"""
    STEADY = "steady"
    CAUTION = "caution"
    URGENT = "urgent"


# Daily Command Center models
class Application(BaseModel):
    id: str
    company: str
    role_title: str
    fit_score: int = Field(ge=0, le=100)
    stage: str  # applied|screen|onsite|offer|rejected
    last_activity_date: str  # ISO date
    has_outreach: bool = False


class TasksPrioritizeRequest(BaseModel):
    applications: List[Application]
    today: str  # ISO date


class Task(BaseModel):
    type: str  # apply|follow_up|outreach
    application_id: str
    priority: int = Field(ge=1, le=3)
    reason: str
    suggested_message_stub: Optional[str] = None


class TasksPrioritizeResponse(BaseModel):
    tasks: List[Task]


# Outcome logging models
class OutcomeLogRequest(BaseModel):
    application_id: str
    stage: str  # applied|viewed|replied|interview|offer|rejected
    outcome: str
    date: str  # ISO date


class StrategyReviewRequest(BaseModel):
    applications: List[dict]
    outcomes: List[dict]


class StrategyReviewResponse(BaseModel):
    insights: List[str]
    recommendations: List[str]


# Tracker Intelligence models
class TrackerApplication(BaseModel):
    """Application data for tracker intelligence"""
    id: str
    status: str
    company: str
    role: str
    date_applied: Optional[str] = None
    decision_confidence: Optional[int] = None
    jd_source: Optional[str] = None
    fit_score: Optional[int] = None
    last_activity_date: Optional[str] = None
    days_since_last_activity: Optional[int] = None
    interview_count: Optional[int] = 0
    substatus: Optional[str] = None
    manual_lock: Optional[bool] = False
    user_override: Optional[bool] = False
    user_override_reason: Optional[str] = None


class OneClickAction(BaseModel):
    """One-click action for quick execution"""
    type: str  # draft_email, archive, open_prep, block_time
    template: Optional[str] = None
    application_id: Optional[str] = None
    confirm: Optional[bool] = False


class PriorityAction(BaseModel):
    """Priority action for an application"""
    application_id: str
    action: str
    reason: str
    priority: PriorityLevel
    one_click_action: Optional[OneClickAction] = None


class PipelineHealth(BaseModel):
    """Pipeline health assessment"""
    active_count: int
    status: PipelineStatus
    color: str
    icon: str
    tone: PipelineTone
    recommendation: str
    reason: str
    priority_count: int = 0


class FocusModeAction(BaseModel):
    """Action to display in focus mode"""
    application_id: str
    company: str
    action: str


class FocusMode(BaseModel):
    """Focus mode configuration"""
    enabled: bool = True
    top_actions: List[FocusModeAction]
    dim_others: bool = True


class UISignals(BaseModel):
    """UI-ready signals for frontend binding"""
    priority: PriorityLevel
    confidence: str  # high, medium, low
    urgency: UrgencyLevel
    color_code: str  # green, yellow, red, gray
    icon: str
    badge: Optional[ConfidenceLabel] = None
    action_available: bool = False
    dimmed: bool = False


class TrackerIntelligenceRequest(BaseModel):
    """Request for tracker intelligence calculation"""
    user_id: str
    applications: List[TrackerApplication]


class ApplicationWithIntelligence(BaseModel):
    """Application with calculated intelligence"""
    id: str
    next_action: str
    next_action_reason: str
    priority_level: PriorityLevel
    one_click_action: Optional[OneClickAction] = None
    ui_signals: UISignals
    decision_confidence: int
    days_since_last_activity: int
    substatus: str


class TrackerIntelligenceResponse(BaseModel):
    """Response from tracker intelligence engine"""
    priority_actions: List[PriorityAction]
    pipeline_health: PipelineHealth
    focus_mode: FocusMode
    applications: List[ApplicationWithIntelligence]


# Confidence calculation models
class CalculateConfidenceRequest(BaseModel):
    """Request to calculate decision confidence"""
    application_id: str
    fit_score: int
    jd_source: str
    days_since_applied: int
    status: str
    interview_count: int = 0
    response_time_days: Optional[int] = None
    days_since_last_activity: Optional[int] = None


class ConfidenceFactors(BaseModel):
    """Factors used in confidence calculation"""
    alignment_score: int
    momentum_score: int
    jd_confidence: int


class CalculateConfidenceResponse(BaseModel):
    """Response with calculated confidence"""
    decision_confidence: int
    label: str  # high, medium, low
    factors: ConfidenceFactors
    guidance: str
