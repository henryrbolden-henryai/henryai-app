"""Hey Henry chatbot Pydantic models"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class HeyHenryContext(BaseModel):
    """Context about where the user is in the app."""
    current_page: str
    page_description: str
    company: Optional[str] = None
    role: Optional[str] = None
    has_analysis: bool = False
    has_resume: bool = False
    has_pipeline: bool = False
    has_attachments: bool = False
    user_name: Optional[str] = None
    # Emotional state fields (from frontend)
    emotional_state: Optional[str] = None  # zen, stressed, struggling, desperate, crushed
    confidence_level: Optional[str] = None  # low, need_validation, shaky, strong
    timeline: Optional[str] = None  # urgent, soon, actively_looking, no_rush
    tone_guidance: Optional[str] = None  # Generated guidance string from frontend
    # Clarification detection (from frontend)
    needs_clarification: bool = False
    clarification_hints: Optional[List[Dict[str, str]]] = None


class HeyHenryMessage(BaseModel):
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class HeyHenryAttachment(BaseModel):
    """An attachment sent with a Hey Henry message."""
    name: str
    type: str  # MIME type
    size: int
    data: str  # Base64 encoded


class HeyHenryRequest(BaseModel):
    """Request for Hey Henry chat."""
    message: str
    conversation_history: List[HeyHenryMessage] = []
    context: HeyHenryContext
    analysis_data: Optional[Dict[str, Any]] = None
    resume_data: Optional[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None  # Includes emotional state/situation
    pipeline_data: Optional[Dict[str, Any]] = None  # Application pipeline metrics and apps
    attachments: Optional[List[HeyHenryAttachment]] = None  # File attachments (images, documents)
    # Generated content - Henry is the AUTHOR of these
    documents_data: Optional[Dict[str, Any]] = None  # Generated resume, cover letter, changes
    outreach_data: Optional[Dict[str, Any]] = None  # Generated outreach templates
    interview_prep_data: Optional[Dict[str, Any]] = None  # Generated interview prep modules
    positioning_data: Optional[Dict[str, Any]] = None  # Positioning strategy content
    # Network data - LinkedIn connections (Phase 2.1)
    network_data: Optional[Dict[str, Any]] = None  # LinkedIn connections at target company
    # Outreach log data - Follow-up tracking (Phase 2.7)
    outreach_log_data: Optional[Dict[str, Any]] = None  # Outreach tracking and follow-ups
    # Interview debrief data - Missing debrief detection (Phase 2.3)
    interview_debrief_data: Optional[Dict[str, Any]] = None  # Interviews needing debriefs
    # Cross-interview pattern analysis (Phase 2.3)
    debrief_pattern_analysis: Optional[Dict[str, Any]] = None  # Patterns across user's debriefs


class HeyHenryResponse(BaseModel):
    """Response from Hey Henry."""
    response: str


# Backwards compatibility alias
AskHenryContext = HeyHenryContext
