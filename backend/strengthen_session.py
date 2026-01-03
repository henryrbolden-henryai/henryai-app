"""
Strengthen Your Resume - Session Management and Remediation Logic

This module handles:
- Strengthen session creation and management
- Guided bullet regeneration with constraints
- Forbidden input detection and validation
- Audit trail for all regenerations
- NEW: Tag-based bullet verification system (VERIFIED, VAGUE, RISKY, IMPLAUSIBLE)
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


# ============================================================================
# FORBIDDEN INPUT PATTERNS
# ============================================================================

FORBIDDEN_PATTERNS = [
    # New accomplishments
    (r"\b(I also|additionally I|I additionally)\b.*\b(did|led|managed|created|built|launched|developed)\b", "new_accomplishment"),
    (r"\b(another thing|one more thing|I forgot to mention)\b", "new_accomplishment"),

    # Title changes
    (r"\b(promoted to|became|was made|got promoted|moved up to)\b", "title_change"),
    (r"\b(my title changed|they gave me|I was given the title)\b", "title_change"),

    # New skills
    (r"\b(learned|picked up|started using|taught myself|self-taught)\b.*\b(how to|the skill|programming|coding)\b", "new_skill"),
    (r"\b(I know|I can also|I'm also proficient in)\b", "new_skill"),

    # New companies/experiences
    (r"\b(worked at|joined|started at|I was at|my time at)\b(?!.*\b(the same|this|that)\b)", "new_company"),
    (r"\b(before that|after that|in between|at another company)\b", "new_company"),
]

# Implausible metric thresholds by context
IMPLAUSIBLE_THRESHOLDS = {
    "revenue_impact_entry": 1_000_000,       # $1M+ for entry-level suspicious
    "revenue_impact_mid": 10_000_000,        # $10M+ for mid-level suspicious
    "revenue_impact_senior": 100_000_000,    # $100M+ for senior suspicious
    "team_size_ic": 50,                      # 50+ reports for IC suspicious
    "team_size_manager": 200,                # 200+ for manager suspicious
    "percentage_improvement": 500,            # 500%+ improvement suspicious
    "cost_savings_entry": 500_000,           # $500K savings for entry suspicious
    "users_impacted_startup": 10_000_000,    # 10M users for startup suspicious
}


# ============================================================================
# NEW TAG-BASED SYSTEM (from Strengthen Your Resume spec)
# ============================================================================

class BulletTag(str, Enum):
    """Verification tag for resume bullets - from leveling analysis"""
    VERIFIED = "VERIFIED"      # Has metrics, clear ownership, no credibility concerns
    VAGUE = "VAGUE"            # Missing metrics, unclear ownership, generic language
    RISKY = "RISKY"            # Scope inflated for role/tenure, title mismatch
    IMPLAUSIBLE = "IMPLAUSIBLE"  # IC claiming exec scope, impossible metrics


class ClarificationType(str, Enum):
    """What type of clarification is needed"""
    OWNERSHIP = "ownership"    # Who owned vs contributed
    SCOPE = "scope"            # Size/scale of impact
    OUTCOME = "outcome"        # Measurable results


class ConfidenceLevel(str, Enum):
    """Confidence level for enhancements"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


# ============================================================================
# LEGACY ENUMS (kept for backward compatibility with existing endpoints)
# ============================================================================

class IssuePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(str, Enum):
    MISSING_METRICS = "missing_metrics"
    VAGUE_OWNERSHIP = "vague_ownership"
    NO_SCOPE = "no_scope"
    WEAK_IMPACT = "weak_impact"
    TECHNICAL_DEPTH = "technical_depth"
    LEADERSHIP_UNCLEAR = "leadership_unclear"


# ============================================================================
# NEW TAG-BASED DATACLASSES
# ============================================================================

@dataclass
class BulletAuditItem:
    """A single audited bullet from the leveling analysis"""
    id: str  # e.g., "exp-0-bullet-0"
    text: str  # The exact bullet text
    section: str  # e.g., "Experience - Acme Corp, PM"
    tag: BulletTag
    issues: List[str]  # Empty if VERIFIED
    clarifies: ClarificationType

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "section": self.section,
            "tag": self.tag.value,
            "issues": self.issues,
            "clarifies": self.clarifies.value,
        }


@dataclass
class StrengthenQuestionItem:
    """A clarifying question for a flagged bullet"""
    bullet_id: str
    original_bullet: str
    tag: BulletTag
    question: str
    clarifies: ClarificationType
    answer: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bullet_id": self.bullet_id,
            "original_bullet": self.original_bullet,
            "tag": self.tag.value,
            "question": self.question,
            "clarifies": self.clarifies.value,
            "answer": self.answer,
        }


@dataclass
class EnhancementResult:
    """Result of applying an enhancement to a bullet"""
    bullet_id: str
    original_bullet: str
    enhanced_bullet: str
    confidence: ConfidenceLevel
    changes_made: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bullet_id": self.bullet_id,
            "original_bullet": self.original_bullet,
            "enhanced_bullet": self.enhanced_bullet,
            "confidence": self.confidence.value,
            "changes_made": self.changes_made,
        }


@dataclass
class DeclinedBullet:
    """A bullet that was declined by the candidate"""
    bullet_id: str
    original_bullet: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bullet_id": self.bullet_id,
            "original_bullet": self.original_bullet,
            "reason": self.reason,
        }


@dataclass
class UnresolvedBullet:
    """A bullet that couldn't be resolved"""
    bullet_id: str
    original_bullet: str
    tag: BulletTag
    reason: str = "No clarification provided"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bullet_id": self.bullet_id,
            "original_bullet": self.original_bullet,
            "tag": self.tag.value,
            "reason": self.reason,
        }


# ============================================================================
# LEGACY DATACLASSES (kept for backward compatibility)
# ============================================================================

@dataclass
class StrengthenIssue:
    """A single issue identified for strengthening."""
    issue_id: str
    issue_type: IssueType
    priority: IssuePriority
    original_bullet: str
    role_context: str  # e.g., "Product Manager at Acme Inc"
    what_is_missing: str
    clarifying_questions: List[str]
    addressed: bool = False
    skipped: bool = False
    skip_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type.value,
            "priority": self.priority.value,
            "original_bullet": self.original_bullet,
            "role_context": self.role_context,
            "what_is_missing": self.what_is_missing,
            "clarifying_questions": self.clarifying_questions,
            "addressed": self.addressed,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
        }


@dataclass
class BulletRegeneration:
    """A single regeneration attempt for a bullet."""
    regeneration_id: str
    issue_id: str
    original_bullet: str
    user_inputs: Dict[str, str]
    generated_bullet: str
    what_changed: List[str]
    generation_number: int  # 1, 2, or 3
    accepted: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "regeneration_id": self.regeneration_id,
            "issue_id": self.issue_id,
            "original_bullet": self.original_bullet,
            "user_inputs": self.user_inputs,
            "generated_bullet": self.generated_bullet,
            "what_changed": self.what_changed,
            "generation_number": self.generation_number,
            "accepted": self.accepted,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class StrengthenSession:
    """A complete strengthen session."""
    session_id: str
    resume_id: str
    issues: List[StrengthenIssue]
    regenerations: List[BulletRegeneration] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def get_issue(self, issue_id: str) -> Optional[StrengthenIssue]:
        for issue in self.issues:
            if issue.issue_id == issue_id:
                return issue
        return None

    def get_regeneration_count(self, issue_id: str) -> int:
        return len([r for r in self.regenerations if r.issue_id == issue_id])

    def get_progress(self) -> Dict[str, Any]:
        total = len(self.issues)
        addressed = len([i for i in self.issues if i.addressed])
        skipped = len([i for i in self.issues if i.skipped])
        remaining = total - addressed - skipped

        return {
            "total_issues": total,
            "addressed": addressed,
            "skipped": skipped,
            "remaining": remaining,
            "percent_complete": round((addressed + skipped) / total * 100) if total > 0 else 100,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "resume_id": self.resume_id,
            "issues": [i.to_dict() for i in self.issues],
            "regenerations": [r.to_dict() for r in self.regenerations],
            "progress": self.get_progress(),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ============================================================================
# INPUT VALIDATION
# ============================================================================

@dataclass
class ValidationResult:
    """Result of input validation."""
    valid: bool
    forbidden_type: Optional[str] = None
    forbidden_match: Optional[str] = None
    implausible_metric: Optional[str] = None
    message: Optional[str] = None


def validate_user_input(
    user_input: str,
    input_type: str,
    candidate_level: str = "mid"
) -> ValidationResult:
    """
    Validate user input against forbidden patterns and implausible metrics.

    Args:
        user_input: The text provided by the user
        input_type: Type of input (metric, team_size, scope, etc.)
        candidate_level: Level for threshold checking (entry, mid, senior)

    Returns:
        ValidationResult with valid flag and details if invalid
    """
    # Check forbidden patterns
    for pattern, forbidden_type in FORBIDDEN_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            match = re.search(pattern, user_input, re.IGNORECASE)
            return ValidationResult(
                valid=False,
                forbidden_type=forbidden_type,
                forbidden_match=match.group(0) if match else None,
                message=_get_forbidden_message(forbidden_type)
            )

    # Check implausible metrics
    if input_type in ("metric", "revenue", "savings", "impact"):
        implausible = _check_implausible_metric(user_input, candidate_level)
        if implausible:
            return ValidationResult(
                valid=False,
                implausible_metric=implausible,
                message=f"This metric seems unusually high. Can you verify: {implausible}?"
            )

    # Check team size
    if input_type == "team_size":
        implausible = _check_implausible_team_size(user_input, candidate_level)
        if implausible:
            return ValidationResult(
                valid=False,
                implausible_metric=implausible,
                message="This team size seems unusually large for your level. Can you clarify?"
            )

    return ValidationResult(valid=True)


def _get_forbidden_message(forbidden_type: str) -> str:
    """Get user-friendly message for forbidden input type."""
    messages = {
        "new_accomplishment": "We can only strengthen existing bullets, not add new accomplishments. Please provide context about what's already on your resume.",
        "title_change": "We can't modify job titles. Please provide metrics or context for your existing role.",
        "new_skill": "We can only clarify skills already demonstrated in your resume. Adding new skills is outside the scope of strengthening.",
        "new_company": "We can only strengthen experience from companies already on your resume.",
    }
    return messages.get(forbidden_type, "This input type is not allowed in the strengthen flow.")


def _check_implausible_metric(user_input: str, level: str) -> Optional[str]:
    """Check if a metric seems implausibly high for the given level."""
    # Extract dollar amounts
    dollar_match = re.search(r'\$[\d,]+(?:\.\d+)?[KMB]?|\d+(?:\.\d+)?\s*(?:million|billion|M|B|K)', user_input, re.IGNORECASE)
    if dollar_match:
        amount = _parse_dollar_amount(dollar_match.group(0))
        threshold_key = f"revenue_impact_{level}"
        threshold = IMPLAUSIBLE_THRESHOLDS.get(threshold_key, IMPLAUSIBLE_THRESHOLDS["revenue_impact_mid"])
        if amount > threshold:
            return f"${amount:,.0f} impact claimed"

    # Extract percentages
    pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', user_input)
    if pct_match:
        pct = float(pct_match.group(1))
        if pct > IMPLAUSIBLE_THRESHOLDS["percentage_improvement"]:
            return f"{pct}% improvement claimed"

    return None


def _check_implausible_team_size(user_input: str, level: str) -> Optional[str]:
    """Check if team size seems implausibly large."""
    size_match = re.search(r'(\d+)\s*(?:people|reports|team members|engineers|designers)?', user_input)
    if size_match:
        size = int(size_match.group(1))
        threshold_key = "team_size_ic" if level in ("entry", "mid") else "team_size_manager"
        threshold = IMPLAUSIBLE_THRESHOLDS.get(threshold_key, 50)
        if size > threshold:
            return f"{size} direct reports claimed"
    return None


def _parse_dollar_amount(amount_str: str) -> float:
    """Parse a dollar amount string into a float."""
    # Remove $ and commas
    cleaned = re.sub(r'[$,]', '', amount_str)

    # Handle K/M/B suffixes
    multipliers = {'k': 1000, 'm': 1_000_000, 'b': 1_000_000_000}
    for suffix, mult in multipliers.items():
        if suffix in cleaned.lower():
            cleaned = re.sub(r'[KMBkmb]', '', cleaned)
            try:
                return float(cleaned) * mult
            except ValueError:
                return 0

    # Handle "million", "billion" words
    if 'million' in cleaned.lower():
        cleaned = re.sub(r'million', '', cleaned, flags=re.IGNORECASE).strip()
        try:
            return float(cleaned) * 1_000_000
        except ValueError:
            return 0
    if 'billion' in cleaned.lower():
        cleaned = re.sub(r'billion', '', cleaned, flags=re.IGNORECASE).strip()
        try:
            return float(cleaned) * 1_000_000_000
        except ValueError:
            return 0

    try:
        return float(cleaned)
    except ValueError:
        return 0


# ============================================================================
# SESSION STORE (In-Memory)
# ============================================================================

class StrengthenSessionStore:
    """In-memory store for strengthen sessions."""

    def __init__(self):
        self._sessions: Dict[str, StrengthenSession] = {}

    def create_session(
        self,
        resume_id: str,
        issues: List[Dict[str, Any]]
    ) -> StrengthenSession:
        """Create a new strengthen session from identified issues."""
        session_id = str(uuid.uuid4())[:12]

        strengthen_issues = []
        for i, issue_data in enumerate(issues):
            issue = StrengthenIssue(
                issue_id=f"{session_id}-{i}",
                issue_type=IssueType(issue_data.get("type", "missing_metrics")),
                priority=IssuePriority(issue_data.get("priority", "medium")),
                original_bullet=issue_data.get("bullet", ""),
                role_context=issue_data.get("role_context", ""),
                what_is_missing=issue_data.get("what_is_missing", ""),
                clarifying_questions=issue_data.get("clarifying_questions", []),
            )
            strengthen_issues.append(issue)

        session = StrengthenSession(
            session_id=session_id,
            resume_id=resume_id,
            issues=strengthen_issues,
        )

        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[StrengthenSession]:
        return self._sessions.get(session_id)

    def add_regeneration(
        self,
        session_id: str,
        issue_id: str,
        user_inputs: Dict[str, str],
        generated_bullet: str,
        what_changed: List[str]
    ) -> Optional[BulletRegeneration]:
        """Add a regeneration to a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        issue = session.get_issue(issue_id)
        if not issue:
            return None

        gen_number = session.get_regeneration_count(issue_id) + 1
        if gen_number > 3:
            return None  # Max regenerations reached

        regeneration = BulletRegeneration(
            regeneration_id=str(uuid.uuid4())[:8],
            issue_id=issue_id,
            original_bullet=issue.original_bullet,
            user_inputs=user_inputs,
            generated_bullet=generated_bullet,
            what_changed=what_changed,
            generation_number=gen_number,
        )

        session.regenerations.append(regeneration)
        return regeneration

    def accept_regeneration(
        self,
        session_id: str,
        issue_id: str,
        regeneration_id: str
    ) -> bool:
        """Mark a regeneration as accepted and issue as addressed."""
        session = self.get_session(session_id)
        if not session:
            return False

        issue = session.get_issue(issue_id)
        if not issue:
            return False

        for regen in session.regenerations:
            if regen.regeneration_id == regeneration_id:
                regen.accepted = True
                issue.addressed = True
                return True

        return False

    def skip_issue(
        self,
        session_id: str,
        issue_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Mark an issue as skipped."""
        session = self.get_session(session_id)
        if not session:
            return False

        issue = session.get_issue(issue_id)
        if not issue:
            return False

        issue.skipped = True
        issue.skip_reason = reason
        return True

    def complete_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Mark session complete and return summary."""
        session = self.get_session(session_id)
        if not session:
            return None

        session.completed_at = datetime.now()

        # Build before/after summary
        improvements = []
        for regen in session.regenerations:
            if regen.accepted:
                improvements.append({
                    "original": regen.original_bullet,
                    "improved": regen.generated_bullet,
                    "what_changed": regen.what_changed,
                })

        return {
            "session_id": session_id,
            "completed_at": session.completed_at.isoformat(),
            "progress": session.get_progress(),
            "improvements": improvements,
            "issues_skipped": [
                {"bullet": i.original_bullet, "reason": i.skip_reason}
                for i in session.issues if i.skipped
            ],
        }


# Global store instance
_strengthen_store: Optional[StrengthenSessionStore] = None


def get_strengthen_store() -> StrengthenSessionStore:
    """Get or create the global strengthen session store."""
    global _strengthen_store
    if _strengthen_store is None:
        _strengthen_store = StrengthenSessionStore()
    return _strengthen_store


# ============================================================================
# ISSUE EXTRACTION FROM LINT/QUALITY RESULTS
# ============================================================================

def extract_strengthen_issues(
    lint_results: Dict[str, Any],
    quality_gates: Optional[Dict[str, Any]] = None,
    resume_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Extract strengthen issues from lint results and quality gates.

    Converts flagged bullets and quality gate failures into actionable
    strengthen issues with clarifying questions.
    """
    issues = []

    # Extract from lint results
    flagged = lint_results.get("flagged_bullets", [])
    for flag in flagged:
        severity = flag.get("severity", "medium")
        priority = {
            "high": IssuePriority.HIGH,
            "medium": IssuePriority.MEDIUM,
            "low": IssuePriority.LOW,
        }.get(severity, IssuePriority.MEDIUM)

        # Map lint rule to issue type
        rule = flag.get("rule", "")
        issue_type = _map_rule_to_issue_type(rule)

        # Generate clarifying questions based on issue type
        questions = _generate_clarifying_questions(issue_type, flag.get("bullet", ""))

        issues.append({
            "type": issue_type.value,
            "priority": priority.value,
            "bullet": flag.get("bullet", ""),
            "role_context": flag.get("role", ""),
            "what_is_missing": flag.get("suggested_fix", flag.get("reason", "")),
            "clarifying_questions": questions,
        })

    # Extract from quality gates if provided
    if quality_gates:
        signal_contract = quality_gates.get("signal_contract", {})
        if not signal_contract.get("valid", True):
            missing = signal_contract.get("missing_signals", [])
            for signal in missing:
                issue_type = _map_signal_to_issue_type(signal)
                issues.append({
                    "type": issue_type.value,
                    "priority": IssuePriority.HIGH.value,
                    "bullet": "",  # General issue, not bullet-specific
                    "role_context": "",
                    "what_is_missing": f"Resume lacks {signal} signals",
                    "clarifying_questions": _generate_signal_questions(signal),
                })

    # Sort by priority
    priority_order = {IssuePriority.HIGH.value: 0, IssuePriority.MEDIUM.value: 1, IssuePriority.LOW.value: 2}
    issues.sort(key=lambda x: priority_order.get(x["priority"], 1))

    return issues


def _map_rule_to_issue_type(rule: str) -> IssueType:
    """Map a lint rule to an issue type."""
    rule_lower = rule.lower()
    if "metric" in rule_lower or "quantif" in rule_lower:
        return IssueType.MISSING_METRICS
    elif "ownership" in rule_lower or "vague" in rule_lower or "passive" in rule_lower:
        return IssueType.VAGUE_OWNERSHIP
    elif "scope" in rule_lower:
        return IssueType.NO_SCOPE
    elif "impact" in rule_lower:
        return IssueType.WEAK_IMPACT
    elif "technical" in rule_lower or "depth" in rule_lower:
        return IssueType.TECHNICAL_DEPTH
    elif "leadership" in rule_lower or "team" in rule_lower:
        return IssueType.LEADERSHIP_UNCLEAR
    return IssueType.VAGUE_OWNERSHIP


def _map_signal_to_issue_type(signal: str) -> IssueType:
    """Map a quality gate signal to an issue type."""
    signal_lower = signal.lower()
    if "scope" in signal_lower:
        return IssueType.NO_SCOPE
    elif "impact" in signal_lower:
        return IssueType.WEAK_IMPACT
    elif "ownership" in signal_lower:
        return IssueType.VAGUE_OWNERSHIP
    elif "level" in signal_lower:
        return IssueType.LEADERSHIP_UNCLEAR
    return IssueType.MISSING_METRICS


def _generate_clarifying_questions(issue_type: IssueType, bullet: str) -> List[str]:
    """Generate contextual clarifying questions for an issue type."""
    questions = {
        IssueType.MISSING_METRICS: [
            "What was the measurable result? (percentage, dollar amount, time saved)",
            "How many users/customers/stakeholders were impacted?",
            "What was the before and after comparison?",
        ],
        IssueType.VAGUE_OWNERSHIP: [
            "Were you the primary owner or a contributor?",
            "Did you make the final decisions or provide recommendations?",
            "Who else was involved and what was your specific role?",
        ],
        IssueType.NO_SCOPE: [
            "How large was the project scope? (budget, team size, timeline)",
            "What was the geographic or organizational reach?",
            "How many stakeholders or departments were involved?",
        ],
        IssueType.WEAK_IMPACT: [
            "What business outcome did this drive?",
            "How did this affect revenue, costs, or efficiency?",
            "What would have happened without this work?",
        ],
        IssueType.TECHNICAL_DEPTH: [
            "What technologies or methodologies did you use?",
            "What technical challenges did you solve?",
            "What was the technical complexity or scale?",
        ],
        IssueType.LEADERSHIP_UNCLEAR: [
            "How large was the team you led or influenced?",
            "What was your management or mentorship role?",
            "Did you have hiring, performance review, or strategic responsibilities?",
        ],
    }
    return questions.get(issue_type, ["Can you provide more context about this experience?"])


def _generate_signal_questions(signal: str) -> List[str]:
    """Generate questions to address a missing quality gate signal."""
    signal_lower = signal.lower()
    if "scope" in signal_lower:
        return [
            "Tell us about the largest project you've managed - what was its scope?",
            "What's the biggest budget or team you've been responsible for?",
        ]
    elif "impact" in signal_lower:
        return [
            "What's the most significant business outcome you've driven?",
            "Can you share a specific metric that demonstrates your impact?",
        ]
    elif "ownership" in signal_lower:
        return [
            "Describe a project where you were the sole decision-maker",
            "What's an initiative you owned end-to-end?",
        ]
    return ["Can you provide more context about your experience?"]


# ============================================================================
# BULLET REGENERATION LOGIC
# ============================================================================

def build_regeneration_prompt(
    original_bullet: str,
    issue_type: IssueType,
    user_inputs: Dict[str, str],
    role_context: str
) -> str:
    """
    Build a prompt for Claude to regenerate a strengthened bullet.

    The prompt constrains Claude to only use information provided,
    not invent new details.
    """
    input_summary = "\n".join([f"- {k}: {v}" for k, v in user_inputs.items()])

    return f"""You are helping strengthen a resume bullet point. You must ONLY use the information provided below - do not invent or assume any details.

ORIGINAL BULLET:
"{original_bullet}"

ROLE CONTEXT: {role_context}

ISSUE TO ADDRESS: {issue_type.value}

INFORMATION PROVIDED BY CANDIDATE:
{input_summary}

CONSTRAINTS:
1. Only incorporate details explicitly provided above
2. Keep the core accomplishment the same
3. Do not add new accomplishments or skills
4. Do not change the job title or company
5. Use active voice and strong action verbs
6. Keep the bullet concise (under 2 lines)

Return a JSON object with:
{{
  "strengthened_bullet": "The improved bullet text",
  "what_changed": ["List of specific changes made"]
}}

Return ONLY the JSON, no other text."""


# ============================================================================
# NEW: TAG-BASED HELPER FUNCTIONS
# ============================================================================

def extract_flagged_bullets(leveling_data: Dict[str, Any]) -> List[BulletAuditItem]:
    """
    Extract non-VERIFIED bullets from leveling analysis bullet_audit.

    Args:
        leveling_data: The full leveling analysis response containing bullet_audit

    Returns:
        List of BulletAuditItem for bullets that need clarification
    """
    bullet_audit = leveling_data.get("bullet_audit", [])
    flagged = []

    for item in bullet_audit:
        tag_str = item.get("tag", "VAGUE").upper()
        if tag_str == "VERIFIED":
            continue

        try:
            tag = BulletTag(tag_str)
        except ValueError:
            tag = BulletTag.VAGUE

        clarifies_str = item.get("clarifies", "outcome").lower()
        try:
            clarifies = ClarificationType(clarifies_str)
        except ValueError:
            clarifies = ClarificationType.OUTCOME

        flagged.append(BulletAuditItem(
            id=item.get("id", ""),
            text=item.get("text", ""),
            section=item.get("section", ""),
            tag=tag,
            issues=item.get("issues", []),
            clarifies=clarifies,
        ))

    # Sort by priority: IMPLAUSIBLE first, then RISKY, then VAGUE
    priority_order = {
        BulletTag.IMPLAUSIBLE: 0,
        BulletTag.RISKY: 1,
        BulletTag.VAGUE: 2,
    }
    flagged.sort(key=lambda x: priority_order.get(x.tag, 2))

    return flagged


def should_auto_skip_strengthen(leveling_data: Dict[str, Any]) -> bool:
    """
    Check if strengthen step should be auto-skipped (all bullets VERIFIED).

    Args:
        leveling_data: The full leveling analysis response

    Returns:
        True if all bullets are VERIFIED and strengthen can be skipped
    """
    bullet_audit = leveling_data.get("bullet_audit", [])

    if not bullet_audit:
        return False  # No audit data, don't skip

    for item in bullet_audit:
        tag = item.get("tag", "").upper()
        if tag != "VERIFIED":
            return False

    return True


def map_tag_to_priority(tag: BulletTag) -> IssuePriority:
    """Map new tag system to legacy priority for backward compatibility."""
    mapping = {
        BulletTag.IMPLAUSIBLE: IssuePriority.HIGH,
        BulletTag.RISKY: IssuePriority.HIGH,
        BulletTag.VAGUE: IssuePriority.MEDIUM,
        BulletTag.VERIFIED: IssuePriority.LOW,
    }
    return mapping.get(tag, IssuePriority.MEDIUM)


def map_clarification_to_issue_type(clarifies: ClarificationType) -> IssueType:
    """Map new clarification type to legacy issue type."""
    mapping = {
        ClarificationType.OWNERSHIP: IssueType.VAGUE_OWNERSHIP,
        ClarificationType.SCOPE: IssueType.NO_SCOPE,
        ClarificationType.OUTCOME: IssueType.MISSING_METRICS,
    }
    return mapping.get(clarifies, IssueType.VAGUE_OWNERSHIP)


def format_bullets_for_prompt(bullets: List[BulletAuditItem]) -> str:
    """
    Format flagged bullets for inclusion in a Claude prompt.

    Args:
        bullets: List of BulletAuditItem to format

    Returns:
        Formatted string for prompt inclusion
    """
    lines = []
    for bullet in bullets:
        lines.append(f"""
Bullet ID: {bullet.id}
Section: {bullet.section}
Text: "{bullet.text}"
Tag: {bullet.tag.value}
Issues: {', '.join(bullet.issues) if bullet.issues else 'None specified'}
Needs clarification on: {bullet.clarifies.value}
""")
    return "\n".join(lines)


def format_answers_for_prompt(answers: List[Dict[str, Any]]) -> str:
    """
    Format candidate answers for inclusion in enhancement prompt.

    Args:
        answers: List of answer dictionaries with bullet_id, original_bullet, answer, tag

    Returns:
        Formatted string for prompt inclusion
    """
    lines = []
    for ans in answers:
        answer_text = ans.get("answer", "").strip()
        if not answer_text or answer_text.lower() in ["no", "n/a", "none", "i don't have that", "skip"]:
            status = "DECLINED/SKIPPED"
        else:
            status = "PROVIDED"

        lines.append(f"""
Bullet ID: {ans.get('bullet_id', '')}
Original: "{ans.get('original_bullet', '')}"
Tag: {ans.get('tag', 'VAGUE')}
Candidate's Answer: "{answer_text}"
Status: {status}
""")
    return "\n".join(lines)


def validate_answer_for_fabrication(answer: str, candidate_level: str = "mid") -> ValidationResult:
    """
    Validate a candidate's answer for fabrication attempts.

    Combines forbidden pattern detection with implausibility checks.

    Args:
        answer: The candidate's answer text
        candidate_level: Level for threshold checking (entry, mid, senior)

    Returns:
        ValidationResult with valid flag and details if invalid
    """
    # First check forbidden patterns
    result = validate_user_input(answer, "general", candidate_level)
    if not result.valid:
        return result

    # Then check for implausible metrics in the answer
    result = validate_user_input(answer, "metric", candidate_level)
    if not result.valid:
        return result

    # Check team size if mentioned
    if re.search(r'\d+\s*(people|reports|team|engineers|designers)', answer, re.IGNORECASE):
        result = validate_user_input(answer, "team_size", candidate_level)
        if not result.valid:
            return result

    return ValidationResult(valid=True)


def build_strengthened_data(
    enhancements: List[EnhancementResult],
    declined: List[DeclinedBullet],
    unresolved: List[UnresolvedBullet],
    questions_asked: int,
    questions_answered: int,
    skipped: bool = False,
    skip_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build the final strengthenedData object for sessionStorage.

    This is the data contract consumed by document generation.

    Args:
        enhancements: List of successful enhancements
        declined: List of declined bullets
        unresolved: List of unresolved bullets
        questions_asked: Total questions presented
        questions_answered: Questions with substantive answers
        skipped: Whether the entire flow was skipped
        skip_reason: Reason for skipping if applicable

    Returns:
        Dictionary matching the strengthenedData schema
    """
    import time

    return {
        "status": "skipped" if skipped else "completed",
        "verified_enhancements": [e.to_dict() for e in enhancements],
        "declined_items": [d.to_dict() for d in declined],
        "unresolved_items": [u.to_dict() for u in unresolved],
        "skipped_reason": skip_reason,
        "questions_asked": questions_asked,
        "questions_answered": questions_answered,
        "timestamp": int(time.time() * 1000),
    }
