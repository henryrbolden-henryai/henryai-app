"""
Pydantic models for Story Bank API endpoints.

Supports:
- AI Mock Story Generation (Core 3 Flow)
- Rules-Based Recommendation Engine
- Story Insights/Analytics
- Templates Library
- Coaching Cues
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


# ============================================
# ENUMS
# ============================================

class StorySource(str, Enum):
    AI_DRAFT = "AI Draft"
    USER = "User"
    TEMPLATE = "Template"


class StoryConfidence(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RoleLevel(str, Enum):
    IC = "IC"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    VP = "VP"
    EXECUTIVE = "Executive"


class InterviewStage(str, Enum):
    RECRUITER_SCREEN = "recruiter_screen"
    HIRING_MANAGER = "hiring_manager"
    TECHNICAL = "technical"
    PANEL = "panel"
    EXECUTIVE = "executive"


class CompanyType(str, Enum):
    BIG_TECH = "big_tech"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    CONSULTING = "consulting"


class CoreCompetency(str, Enum):
    """Core 3 story categories"""
    LEADERSHIP_INFLUENCE = "Leadership / Influence"
    EXECUTION_PROBLEM_SOLVING = "Execution / Problem-Solving"
    FAILURE_CONFLICT = "Failure / Conflict"


# ============================================
# COACHING CUES
# ============================================

class CoachingCues(BaseModel):
    """Coaching cues for story delivery"""
    emphasize: List[str] = Field(default_factory=list, description="1-2 points to emphasize")
    avoid: List[str] = Field(default_factory=list, description="1-2 things to avoid saying")
    stop_talking_when: Optional[str] = Field(None, description="Hard stop signal")
    recovery_line: Optional[str] = Field(None, description="If you want the short version...")


# ============================================
# FEATURE 1: AI STORY GENERATION (Core 3 Flow)
# ============================================

class GenerateStoriesRequest(BaseModel):
    """Request to generate AI draft stories from resume"""
    resume_json: Dict[str, Any]
    resume_id: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    target_role_level: Optional[RoleLevel] = None
    interview_stage: InterviewStage = InterviewStage.HIRING_MANAGER
    competencies: Optional[List[str]] = None
    generate_core_3: bool = Field(default=True, description="Generate Core 3 stories")
    max_stories: int = Field(default=3, ge=1, le=12)


class GeneratedStory(BaseModel):
    """A single AI-generated story"""
    title: str
    opening_line: str = Field(description="One-sentence hook to start")
    demonstrates: List[str]
    situation: str
    task: str
    action: str
    result: str
    best_for_questions: List[str]
    interview_stages: List[str] = []
    role_level: Optional[str] = None
    resume_evidence: Optional[str] = Field(None, description="Resume bullet this story is based on")
    source: str = "AI Draft"
    confidence: str = "Low"
    is_core: bool = False
    core_category: Optional[str] = Field(None, description="Leadership/Execution/Failure if core")
    coaching_cues: CoachingCues = Field(default_factory=CoachingCues)


class GenerateStoriesResponse(BaseModel):
    """Response from story generation"""
    stories: List[GeneratedStory]
    competencies_covered: List[str]
    gaps_identified: List[str] = Field(default_factory=list, description="Competencies not well-covered")
    core_3_generated: bool = False


# ============================================
# FEATURE 2: RECOMMENDATION ENGINE
# ============================================

class RecommendStoriesRequest(BaseModel):
    """Request for story recommendations during prep"""
    user_id: str
    company: str
    role_title: str
    interview_stage: InterviewStage
    role_level: RoleLevel
    company_type: Optional[CompanyType] = None
    competencies_to_focus: Optional[List[str]] = None
    include_conflict_story: bool = Field(default=True, description="Include a conflict/failure story")


class RecommendedStory(BaseModel):
    """A recommended story with scoring details"""
    story_id: str
    story_name: str
    demonstrates: List[str]
    opening_line: Optional[str] = None
    score: float = Field(ge=0, le=100, description="Composite score 0-100")
    recommendation_tier: str = Field(description="Lead with this | Strong backup | Retire soon")
    reason: str
    effectiveness_score: float = 0.0
    freshness_penalty: float = 0.0
    coaching_cues: Optional[CoachingCues] = None
    is_locked: bool = True


class PrepRecommendations(BaseModel):
    """Stories recommended for a specific interview prep"""
    primary_story: Optional[RecommendedStory] = None
    backup_story: Optional[RecommendedStory] = None
    conflict_story: Optional[RecommendedStory] = None
    soft_time_limit_minutes: int = Field(default=2, description="Target time per story by stage")
    coverage_gaps: List[str] = Field(default_factory=list)


class RecommendStoriesResponse(BaseModel):
    """Full recommendation response"""
    primary_recommendations: List[RecommendedStory] = Field(description="Top 3 - Lead with these")
    backup_recommendations: List[RecommendedStory] = Field(description="If probed deeper")
    retire_soon: List[RecommendedStory] = Field(default_factory=list, description="Overused or underperforming")
    coverage_analysis: Dict[str, bool] = Field(default_factory=dict)
    prep_view: PrepRecommendations = Field(default_factory=PrepRecommendations)


# ============================================
# FEATURE 3: STORY INSIGHTS/ANALYTICS
# ============================================

class StoryInsightsRequest(BaseModel):
    """Request for story analytics"""
    user_id: str


class DimensionPerformance(BaseModel):
    """Performance data for a single dimension value"""
    dimension: str  # role_level, company_type, interview_stage
    value: str  # Director, big_tech, hiring_manager
    story_count: int
    uses: int
    avg_effectiveness: float
    top_story: Optional[str] = None
    weakest_story: Optional[str] = None


class StoryInsightsResponse(BaseModel):
    """Analytics on story performance"""
    total_stories: int
    total_uses: int
    locked_stories: int
    avg_effectiveness: float
    by_role_level: List[DimensionPerformance] = []
    by_company_type: List[DimensionPerformance] = []
    by_interview_stage: List[DimensionPerformance] = []
    overused_stories: List[str] = []
    underused_high_performers: List[str] = []
    actionable_insights: List[str] = []


# ============================================
# FEATURE 4: TEMPLATES LIBRARY
# ============================================

class StoryTemplate(BaseModel):
    """A story template"""
    id: str
    template_name: str
    template_category: str
    demonstrates: List[str]
    best_for_questions: List[str]
    situation_prompt: str
    task_prompt: str
    action_prompt: str
    result_prompt: str
    example_story: Optional[str] = None
    target_levels: List[str] = []
    is_premium: bool = True


class ListTemplatesResponse(BaseModel):
    """Response from listing templates"""
    templates: List[StoryTemplate]
    is_premium_locked: bool = Field(description="True if user cannot access premium templates")


class UseTemplateRequest(BaseModel):
    """Request to create a story from a template"""
    template_id: str
    user_responses: Dict[str, str] = Field(description="Keys: situation, task, action, result")
    story_name: Optional[str] = None


class UseTemplateResponse(BaseModel):
    """Response after creating story from template"""
    story_id: str
    story_name: str
    message: str


# ============================================
# STORY LOCKING
# ============================================

class LockStoryRequest(BaseModel):
    """Request to lock a story (enables tracking)"""
    story_id: str


class LockStoryResponse(BaseModel):
    """Response after locking a story"""
    story_id: str
    locked: bool
    locked_at: datetime
    message: str


# ============================================
# PROMOTE AI DRAFT
# ============================================

class PromoteStoryRequest(BaseModel):
    """Request to promote an AI draft to user story"""
    story_id: str
    updates: Optional[Dict[str, Any]] = Field(None, description="Optional edits during promotion")


class PromoteStoryResponse(BaseModel):
    """Response after promoting a story"""
    story_id: str
    source: str
    confidence: str
    locked: bool
    message: str
