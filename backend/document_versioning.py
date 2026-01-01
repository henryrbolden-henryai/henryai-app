"""
Document Versioning and Feedback System - Phase 4

This module provides:
1. Version history for generated documents (resumes, cover letters)
2. User feedback collection on document quality
3. Change tracking between versions
4. Quality scoring on outputs for continuous improvement
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid


# =============================================================================
# 1. VERSION HISTORY
# =============================================================================

class DocumentType(Enum):
    """Types of documents that can be versioned."""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"


@dataclass
class DocumentVersion:
    """A single version of a document."""
    version_id: str
    document_type: DocumentType
    created_at: datetime
    content_hash: str
    content: Dict[str, Any]  # The actual document content
    metadata: Dict[str, Any]  # Generation parameters, fit score, etc.
    parent_version_id: Optional[str] = None  # Previous version if refinement
    changes_from_parent: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> dict:
        return {
            "version_id": self.version_id,
            "document_type": self.document_type.value,
            "created_at": self.created_at.isoformat(),
            "content_hash": self.content_hash,
            "content": self.content,
            "metadata": self.metadata,
            "parent_version_id": self.parent_version_id,
            "changes_from_parent": self.changes_from_parent
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentVersion":
        return cls(
            version_id=data["version_id"],
            document_type=DocumentType(data["document_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            content_hash=data["content_hash"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            parent_version_id=data.get("parent_version_id"),
            changes_from_parent=data.get("changes_from_parent")
        )


def create_content_hash(content: Dict[str, Any]) -> str:
    """Create a hash of document content for comparison."""
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.md5(content_str.encode()).hexdigest()[:12]


def create_document_version(
    document_type: DocumentType,
    content: Dict[str, Any],
    metadata: Dict[str, Any] = None,
    parent_version: Optional[DocumentVersion] = None
) -> DocumentVersion:
    """Create a new document version."""
    version_id = str(uuid.uuid4())[:8]
    content_hash = create_content_hash(content)

    changes = None
    parent_id = None
    if parent_version:
        parent_id = parent_version.version_id
        changes = compute_changes(parent_version.content, content)

    return DocumentVersion(
        version_id=version_id,
        document_type=document_type,
        created_at=datetime.now(),
        content_hash=content_hash,
        content=content,
        metadata=metadata or {},
        parent_version_id=parent_id,
        changes_from_parent=changes
    )


def compute_changes(old_content: Dict[str, Any], new_content: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Compute changes between two versions of a document.
    Returns list of change descriptions.
    """
    changes = []

    # Check summary changes
    old_summary = old_content.get("summary", "")
    new_summary = new_content.get("summary", "")
    if old_summary != new_summary:
        changes.append({
            "type": "summary_rewritten",
            "description": "Summary was rewritten",
            "location": "summary"
        })

    # Check experience bullet changes
    old_experience = old_content.get("experience", [])
    new_experience = new_content.get("experience", [])

    for i, new_role in enumerate(new_experience):
        if i < len(old_experience):
            old_role = old_experience[i]
            company = new_role.get("company", "Unknown")

            old_bullets = set(old_role.get("bullets", []))
            new_bullets = set(new_role.get("bullets", []))

            added = new_bullets - old_bullets
            removed = old_bullets - new_bullets

            if added:
                changes.append({
                    "type": "bullets_added",
                    "description": f"{len(added)} bullet(s) added",
                    "location": f"role:{company}"
                })
            if removed:
                changes.append({
                    "type": "bullets_removed",
                    "description": f"{len(removed)} bullet(s) removed",
                    "location": f"role:{company}"
                })

    # Check skills changes
    old_skills = set(old_content.get("skills", []))
    new_skills = set(new_content.get("skills", []))

    if old_skills != new_skills:
        added_skills = new_skills - old_skills
        removed_skills = old_skills - new_skills
        if added_skills:
            changes.append({
                "type": "skills_added",
                "description": f"Skills added: {', '.join(list(added_skills)[:3])}",
                "location": "skills"
            })
        if removed_skills:
            changes.append({
                "type": "skills_removed",
                "description": f"Skills removed: {', '.join(list(removed_skills)[:3])}",
                "location": "skills"
            })

    return changes


# =============================================================================
# 2. VERSION HISTORY STORE (In-Memory for now)
# =============================================================================

class VersionStore:
    """
    In-memory store for document versions.
    In production, this would be backed by a database.
    """

    def __init__(self):
        self._versions: Dict[str, List[DocumentVersion]] = {}  # session_id -> versions
        self._version_index: Dict[str, DocumentVersion] = {}  # version_id -> version

    def add_version(self, session_id: str, version: DocumentVersion):
        """Add a new version for a session."""
        if session_id not in self._versions:
            self._versions[session_id] = []
        self._versions[session_id].append(version)
        self._version_index[version.version_id] = version

    def get_version(self, version_id: str) -> Optional[DocumentVersion]:
        """Get a specific version by ID."""
        return self._version_index.get(version_id)

    def get_session_versions(self, session_id: str) -> List[DocumentVersion]:
        """Get all versions for a session."""
        return self._versions.get(session_id, [])

    def get_latest_version(self, session_id: str, document_type: DocumentType) -> Optional[DocumentVersion]:
        """Get the latest version of a specific document type for a session."""
        versions = self._versions.get(session_id, [])
        matching = [v for v in versions if v.document_type == document_type]
        if matching:
            return max(matching, key=lambda v: v.created_at)
        return None

    def get_version_history(self, session_id: str, document_type: DocumentType = None) -> List[Dict[str, Any]]:
        """Get version history summary for a session."""
        versions = self._versions.get(session_id, [])
        if document_type:
            versions = [v for v in versions if v.document_type == document_type]

        return [{
            "version_id": v.version_id,
            "document_type": v.document_type.value,
            "created_at": v.created_at.isoformat(),
            "content_hash": v.content_hash,
            "parent_version_id": v.parent_version_id,
            "changes_count": len(v.changes_from_parent) if v.changes_from_parent else 0
        } for v in sorted(versions, key=lambda x: x.created_at, reverse=True)]


# Global version store (would be per-user in production)
_version_store = VersionStore()


def get_version_store() -> VersionStore:
    """Get the global version store."""
    return _version_store


# =============================================================================
# 3. USER FEEDBACK
# =============================================================================

class FeedbackType(Enum):
    """Types of feedback users can provide."""
    QUALITY_RATING = "quality_rating"  # 1-5 stars
    ACCURACY = "accuracy"  # Was it accurate to my experience?
    USEFULNESS = "usefulness"  # Was it useful?
    SPECIFIC_ISSUE = "specific_issue"  # Report a specific problem
    FEATURE_REQUEST = "feature_request"  # Request improvement


@dataclass
class DocumentFeedback:
    """User feedback on a generated document."""
    feedback_id: str
    version_id: str
    document_type: DocumentType
    feedback_type: FeedbackType
    rating: Optional[int] = None  # 1-5 for rating types
    comment: Optional[str] = None
    specific_location: Optional[str] = None  # e.g., "summary", "role:Company"
    issue_category: Optional[str] = None  # e.g., "fabrication", "tone", "length"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "feedback_id": self.feedback_id,
            "version_id": self.version_id,
            "document_type": self.document_type.value,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "comment": self.comment,
            "specific_location": self.specific_location,
            "issue_category": self.issue_category,
            "created_at": self.created_at.isoformat()
        }


class FeedbackStore:
    """In-memory store for feedback."""

    def __init__(self):
        self._feedback: Dict[str, List[DocumentFeedback]] = {}  # version_id -> feedback list

    def add_feedback(self, feedback: DocumentFeedback):
        """Add feedback for a document version."""
        if feedback.version_id not in self._feedback:
            self._feedback[feedback.version_id] = []
        self._feedback[feedback.version_id].append(feedback)

    def get_version_feedback(self, version_id: str) -> List[DocumentFeedback]:
        """Get all feedback for a specific version."""
        return self._feedback.get(version_id, [])

    def get_average_rating(self, version_id: str) -> Optional[float]:
        """Get average quality rating for a version."""
        feedback = self._feedback.get(version_id, [])
        ratings = [f.rating for f in feedback if f.feedback_type == FeedbackType.QUALITY_RATING and f.rating]
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_feedback_summary(self, version_id: str) -> Dict[str, Any]:
        """Get feedback summary for a version."""
        feedback = self._feedback.get(version_id, [])
        if not feedback:
            return {"total_feedback": 0}

        ratings = [f.rating for f in feedback if f.rating]
        issues = [f for f in feedback if f.feedback_type == FeedbackType.SPECIFIC_ISSUE]

        return {
            "total_feedback": len(feedback),
            "average_rating": sum(ratings) / len(ratings) if ratings else None,
            "rating_count": len(ratings),
            "issue_count": len(issues),
            "issue_categories": list(set(f.issue_category for f in issues if f.issue_category)),
            "has_positive_feedback": any(r >= 4 for r in ratings),
            "has_negative_feedback": any(r <= 2 for r in ratings)
        }


# Global feedback store
_feedback_store = FeedbackStore()


def get_feedback_store() -> FeedbackStore:
    """Get the global feedback store."""
    return _feedback_store


def submit_feedback(
    version_id: str,
    document_type: str,
    feedback_type: str,
    rating: int = None,
    comment: str = None,
    specific_location: str = None,
    issue_category: str = None
) -> DocumentFeedback:
    """Submit feedback for a document version."""
    feedback = DocumentFeedback(
        feedback_id=str(uuid.uuid4())[:8],
        version_id=version_id,
        document_type=DocumentType(document_type),
        feedback_type=FeedbackType(feedback_type),
        rating=rating,
        comment=comment,
        specific_location=specific_location,
        issue_category=issue_category
    )

    get_feedback_store().add_feedback(feedback)
    return feedback


# =============================================================================
# 4. QUALITY SCORING
# =============================================================================

@dataclass
class QualityScore:
    """Quality score for a generated document."""
    overall_score: int  # 0-100
    components: Dict[str, int]  # Individual component scores
    flags: List[str]  # Issues that reduced score
    recommendations: List[str]  # How to improve

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "components": self.components,
            "flags": self.flags,
            "recommendations": self.recommendations
        }


def calculate_quality_score(
    document: Dict[str, Any],
    document_type: DocumentType,
    lint_results: Dict[str, Any] = None,
    quality_gates: Dict[str, Any] = None
) -> QualityScore:
    """
    Calculate quality score for a generated document.
    Combines lint results, quality gates, and document-specific checks.
    """
    score = 100
    components = {}
    flags = []
    recommendations = []

    if document_type == DocumentType.RESUME:
        # Resume-specific scoring
        summary = document.get("summary", "")
        experience = document.get("experience", [])

        # Summary quality (20 points)
        summary_score = 20
        if not summary:
            summary_score = 0
            flags.append("Missing summary")
            recommendations.append("Add a professional summary")
        elif len(summary) < 50:
            summary_score = 10
            flags.append("Summary too short")
            recommendations.append("Expand summary to 2-4 sentences")
        components["summary"] = summary_score

        # Experience quality (40 points)
        experience_score = 40
        if not experience:
            experience_score = 0
            flags.append("No experience listed")
        else:
            # Check for quantified bullets
            all_bullets = [b for role in experience for b in role.get("bullets", [])]
            quantified = sum(1 for b in all_bullets if any(c.isdigit() for c in b))
            if len(all_bullets) > 0:
                quant_ratio = quantified / len(all_bullets)
                if quant_ratio < 0.3:
                    experience_score -= 15
                    flags.append("Low quantification rate")
                    recommendations.append("Add metrics to at least 30% of bullets")
        components["experience"] = experience_score

        # Integrate lint results (20 points)
        lint_score = 20
        if lint_results:
            flagged = lint_results.get("flagged_count", 0)
            if flagged > 5:
                lint_score = 5
                flags.append(f"{flagged} language issues flagged")
            elif flagged > 2:
                lint_score = 12
                flags.append(f"{flagged} language issues flagged")
            elif flagged > 0:
                lint_score = 17
        components["language_quality"] = lint_score

        # Integrate quality gates (20 points)
        gates_score = 20
        if quality_gates:
            if not quality_gates.get("signal_contract", {}).get("valid", True):
                gates_score -= 10
                missing = quality_gates.get("signal_contract", {}).get("missing_signals", [])
                flags.append(f"Missing signals: {', '.join(missing)}")
                recommendations.append("Add scope, impact, or ownership signals")

            credibility = quality_gates.get("credibility", {}).get("credibility", "competitive")
            if credibility == "not_credible":
                gates_score -= 10
                flags.append("Low credibility assessment")
            elif credibility == "marginal":
                gates_score -= 5
        components["signal_strength"] = gates_score

        score = sum(components.values())

    elif document_type == DocumentType.COVER_LETTER:
        # Cover letter-specific scoring
        text = document.get("cover_letter_text", "")

        # Length check (25 points)
        length_score = 25
        word_count = len(text.split())
        if word_count < 100:
            length_score = 10
            flags.append("Cover letter too short")
            recommendations.append("Expand to at least 150 words")
        elif word_count > 400:
            length_score = 15
            flags.append("Cover letter too long")
            recommendations.append("Trim to under 350 words")
        components["length"] = length_score

        # Structure check (25 points)
        structure_score = 25
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        mode = document.get("mode", "standard")
        if mode == "executive" and len(paragraphs) > 3:
            structure_score = 15
            flags.append("Executive mode should be 2 paragraphs")
        elif mode == "standard" and len(paragraphs) < 3:
            structure_score = 15
            flags.append("Standard mode should be 3-4 paragraphs")
        components["structure"] = structure_score

        # Content quality (25 points)
        content_score = 25
        generic_phrases = ["i am writing to", "i believe", "i would be honored", "pleased to apply"]
        if any(phrase in text.lower() for phrase in generic_phrases):
            content_score -= 10
            flags.append("Contains generic phrases")
            recommendations.append("Remove cliché phrases")
        components["content"] = content_score

        # Personalization (25 points)
        personalization_score = 25
        # Check if company name is mentioned
        company = document.get("target_company", "")
        if company and company.lower() not in text.lower():
            personalization_score -= 10
            flags.append("Company name not mentioned")
        components["personalization"] = personalization_score

        score = sum(components.values())

    return QualityScore(
        overall_score=max(0, min(100, score)),
        components=components,
        flags=flags,
        recommendations=recommendations
    )


# =============================================================================
# 5. API INTEGRATION HELPERS
# =============================================================================

def track_document_generation(
    session_id: str,
    document_type: str,
    content: Dict[str, Any],
    metadata: Dict[str, Any] = None,
    lint_results: Dict[str, Any] = None,
    quality_gates: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Track a document generation event.
    Creates version, calculates quality score, returns tracking info.
    """
    doc_type = DocumentType(document_type)
    store = get_version_store()

    # Get previous version if exists
    parent = store.get_latest_version(session_id, doc_type)

    # Create new version
    version = create_document_version(
        document_type=doc_type,
        content=content,
        metadata=metadata,
        parent_version=parent
    )

    # Add to store
    store.add_version(session_id, version)

    # Calculate quality score
    quality_score = calculate_quality_score(
        document=content,
        document_type=doc_type,
        lint_results=lint_results,
        quality_gates=quality_gates
    )

    # Include quality score in version metadata
    version.metadata["quality_score"] = quality_score.to_dict()

    return {
        "version_id": version.version_id,
        "version_number": len(store.get_session_versions(session_id)),
        "content_hash": version.content_hash,
        "is_refinement": parent is not None,
        "changes_from_previous": version.changes_from_parent,
        "quality_score": quality_score.to_dict()
    }


def get_document_history(
    session_id: str,
    document_type: str = None
) -> Dict[str, Any]:
    """Get document version history for a session."""
    store = get_version_store()
    doc_type = DocumentType(document_type) if document_type else None

    history = store.get_version_history(session_id, doc_type)

    # Enrich with feedback data
    feedback_store = get_feedback_store()
    for version_info in history:
        feedback_summary = feedback_store.get_feedback_summary(version_info["version_id"])
        version_info["feedback"] = feedback_summary

    return {
        "session_id": session_id,
        "version_count": len(history),
        "versions": history
    }


def restore_version(version_id: str) -> Optional[Dict[str, Any]]:
    """Restore a previous version's content."""
    store = get_version_store()
    version = store.get_version(version_id)

    if version:
        return {
            "version_id": version.version_id,
            "document_type": version.document_type.value,
            "content": version.content,
            "metadata": version.metadata,
            "created_at": version.created_at.isoformat()
        }
    return None
