"""Pydantic models for Strengthen Your Resume API endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class BulletTag(str, Enum):
    """Verification tag for resume bullets"""
    VERIFIED = "VERIFIED"
    VAGUE = "VAGUE"
    RISKY = "RISKY"
    IMPLAUSIBLE = "IMPLAUSIBLE"


class ClarificationType(str, Enum):
    """Type of clarification needed for a bullet"""
    OWNERSHIP = "ownership"
    SCOPE = "scope"
    OUTCOME = "outcome"


class ConfidenceLevel(str, Enum):
    """Confidence level for enhancements"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


# ============================================================================
# Bullet Audit Models (from Leveling)
# ============================================================================

class BulletAuditItem(BaseModel):
    """A single audited bullet from the leveling analysis"""
    id: str = Field(..., description="Unique identifier like 'exp-0-bullet-0'")
    text: str = Field(..., description="The exact bullet text from resume")
    section: str = Field(..., description="Section context like 'Experience - Acme Corp, PM'")
    tag: BulletTag = Field(..., description="Verification tag")
    issues: List[str] = Field(default_factory=list, description="List of issues if not VERIFIED")
    clarifies: ClarificationType = Field(..., description="What type of clarification is needed")


# ============================================================================
# Question Generation Models
# ============================================================================

class FlaggedBullet(BaseModel):
    """A bullet flagged for clarification"""
    id: str
    text: str
    tag: BulletTag
    issues: List[str]
    section: str


class StrengthenQuestionsRequest(BaseModel):
    """Request to generate clarifying questions"""
    flagged_bullets: List[FlaggedBullet]
    resume_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context about the candidate's resume"
    )


class StrengthenQuestion(BaseModel):
    """A single clarifying question for a bullet"""
    bullet_id: str
    original_bullet: str
    tag: BulletTag
    question: str = Field(..., max_length=200, description="Single clarifying question under 25 words")
    clarifies: ClarificationType


class StrengthenQuestionsResponse(BaseModel):
    """Response containing generated questions"""
    questions: List[StrengthenQuestion]


# ============================================================================
# Answer Application Models
# ============================================================================

class BulletAnswer(BaseModel):
    """A candidate's answer to a clarifying question"""
    bullet_id: str
    original_bullet: str
    answer: str = Field(..., description="Candidate's response to the clarifying question")
    tag: BulletTag


class StrengthenApplyRequest(BaseModel):
    """Request to apply enhancements based on answers"""
    answers: List[BulletAnswer]
    resume_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full resume data for context"
    )


class Enhancement(BaseModel):
    """An enhanced bullet based on candidate clarification"""
    bullet_id: str
    original_bullet: str
    enhanced_bullet: str
    confidence: ConfidenceLevel
    changes_made: str = Field(..., description="Brief explanation of what changed")


class DeclinedBullet(BaseModel):
    """A bullet that was declined (candidate confirmed they didn't own it)"""
    bullet_id: str
    original_bullet: str
    reason: str


class UnresolvedBullet(BaseModel):
    """A bullet that couldn't be resolved (no answer provided)"""
    bullet_id: str
    original_bullet: str
    tag: BulletTag
    reason: str = "No clarification provided"


class StrengthenApplyResponse(BaseModel):
    """Response containing applied enhancements"""
    enhancements: List[Enhancement]
    declined: List[DeclinedBullet]
    unresolved: List[UnresolvedBullet]


# ============================================================================
# Session/State Models
# ============================================================================

class VerifiedEnhancement(BaseModel):
    """A verified enhancement stored in session"""
    bullet_id: str
    original_bullet: str
    enhanced_bullet: str
    confidence: ConfidenceLevel
    changes_made: str


class StrengthenedData(BaseModel):
    """Final output stored in sessionStorage"""
    status: str = Field(..., description="'completed' or 'skipped'")
    verified_enhancements: List[VerifiedEnhancement] = Field(default_factory=list)
    declined_items: List[DeclinedBullet] = Field(default_factory=list)
    unresolved_items: List[UnresolvedBullet] = Field(default_factory=list)
    skipped_reason: Optional[str] = None
    questions_asked: int = 0
    questions_answered: int = 0
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
