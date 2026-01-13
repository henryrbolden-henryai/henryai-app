"""
API Usage Tracking Service for HenryHQ

This module provides functions for tracking Claude API token usage and costs.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import Client

from api_pricing import calculate_cost_cents, format_cost

logger = logging.getLogger("henryhq")


# Feature type constants for categorizing API usage
class FeatureType:
    RESUME_GENERATION = "resume_generation"
    COVER_LETTER = "cover_letter"
    JD_ANALYSIS = "jd_analysis"
    MOCK_INTERVIEW = "mock_interview"
    HENRY_CHAT = "henry_chat"
    INTERVIEW_PREP = "interview_prep"
    COMPANY_INTEL = "company_intel"
    LEADERSHIP_ANALYSIS = "leadership_analysis"
    COACHING = "coaching"
    SKILLS_GAP = "skills_gap"
    STORY_BANK = "story_bank"


class ApiUsageService:
    """Service for tracking and querying API usage."""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def track_usage(
        self,
        user_id: str,
        feature_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track an API call's token usage and cost.

        Args:
            user_id: The user who made the request
            feature_type: Category of the API call (e.g., 'resume_generation')
            model: The Claude model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            request_id: Optional unique request identifier
            metadata: Optional additional context

        Returns:
            The created usage record
        """
        cost_cents = calculate_cost_cents(model, input_tokens, output_tokens)

        record = {
            "user_id": user_id,
            "feature_type": feature_type,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_cents": cost_cents,
        }

        if request_id:
            record["request_id"] = request_id

        if metadata:
            record["metadata"] = metadata

        try:
            response = self.supabase.table("api_usage_tracking").insert(record).execute()
            logger.info(
                f"Tracked API usage: user={user_id}, feature={feature_type}, "
                f"tokens={input_tokens}+{output_tokens}, cost={format_cost(cost_cents)}"
            )
            return response.data[0] if response.data else record
        except Exception as e:
            logger.error(f"Failed to track API usage: {e}")
            # Don't fail the request if tracking fails
            return record

    async def get_current_month_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get the user's API usage for the current month.

        Returns:
            Dict with total usage and breakdown by feature
        """
        try:
            # Get start of current month
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Query usage for current month
            response = self.supabase.table("api_usage_tracking").select(
                "feature_type, input_tokens, output_tokens, cost_cents"
            ).eq("user_id", user_id).gte(
                "created_at", month_start.isoformat()
            ).execute()

            records = response.data or []

            # Aggregate totals
            total_input_tokens = sum(r.get("input_tokens", 0) for r in records)
            total_output_tokens = sum(r.get("output_tokens", 0) for r in records)
            total_cost_cents = sum(r.get("cost_cents", 0) for r in records)
            total_requests = len(records)

            # Breakdown by feature
            by_feature = {}
            for record in records:
                feature = record.get("feature_type", "unknown")
                if feature not in by_feature:
                    by_feature[feature] = {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost_cents": 0,
                    }
                by_feature[feature]["requests"] += 1
                by_feature[feature]["input_tokens"] += record.get("input_tokens", 0)
                by_feature[feature]["output_tokens"] += record.get("output_tokens", 0)
                by_feature[feature]["cost_cents"] += record.get("cost_cents", 0)

            return {
                "period": {
                    "start": month_start.isoformat(),
                    "end": None,  # Current month, no end yet
                    "month": now.strftime("%B %Y"),
                },
                "totals": {
                    "requests": total_requests,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens,
                    "cost_cents": total_cost_cents,
                    "cost_formatted": format_cost(total_cost_cents),
                },
                "by_feature": {
                    feature: {
                        **data,
                        "total_tokens": data["input_tokens"] + data["output_tokens"],
                        "cost_formatted": format_cost(data["cost_cents"]),
                    }
                    for feature, data in by_feature.items()
                },
            }
        except Exception as e:
            logger.error(f"Failed to get monthly usage: {e}")
            return {
                "period": {"month": datetime.utcnow().strftime("%B %Y")},
                "totals": {
                    "requests": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost_cents": 0,
                    "cost_formatted": "$0.00",
                },
                "by_feature": {},
            }

    async def get_usage_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get paginated usage history for a user.

        Args:
            user_id: The user ID
            limit: Maximum records to return
            offset: Number of records to skip

        Returns:
            Dict with records and pagination info
        """
        try:
            response = self.supabase.table("api_usage_tracking").select(
                "*"
            ).eq("user_id", user_id).order(
                "created_at", desc=True
            ).range(offset, offset + limit - 1).execute()

            records = response.data or []

            # Format records
            formatted = []
            for r in records:
                formatted.append({
                    "id": r.get("id"),
                    "feature_type": r.get("feature_type"),
                    "model": r.get("model"),
                    "input_tokens": r.get("input_tokens"),
                    "output_tokens": r.get("output_tokens"),
                    "total_tokens": r.get("input_tokens", 0) + r.get("output_tokens", 0),
                    "cost_cents": r.get("cost_cents"),
                    "cost_formatted": format_cost(r.get("cost_cents", 0)),
                    "created_at": r.get("created_at"),
                    "metadata": r.get("metadata"),
                })

            return {
                "records": formatted,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "count": len(formatted),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get usage history: {e}")
            return {
                "records": [],
                "pagination": {"limit": limit, "offset": offset, "count": 0},
            }

    async def get_lifetime_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get lifetime API usage stats for a user.

        Returns:
            Dict with lifetime totals
        """
        try:
            response = self.supabase.table("api_usage_tracking").select(
                "input_tokens, output_tokens, cost_cents"
            ).eq("user_id", user_id).execute()

            records = response.data or []

            total_input = sum(r.get("input_tokens", 0) for r in records)
            total_output = sum(r.get("output_tokens", 0) for r in records)
            total_cost = sum(r.get("cost_cents", 0) for r in records)

            return {
                "lifetime": {
                    "requests": len(records),
                    "input_tokens": total_input,
                    "output_tokens": total_output,
                    "total_tokens": total_input + total_output,
                    "cost_cents": total_cost,
                    "cost_formatted": format_cost(total_cost),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get lifetime usage: {e}")
            return {
                "lifetime": {
                    "requests": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost_cents": 0,
                    "cost_formatted": "$0.00",
                }
            }


# Convenience function for tracking usage without async context
def track_api_usage_sync(
    supabase: Client,
    user_id: str,
    feature_type: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Synchronous version of track_usage for use in non-async contexts.
    """
    cost_cents = calculate_cost_cents(model, input_tokens, output_tokens)

    record = {
        "user_id": user_id,
        "feature_type": feature_type,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_cents": cost_cents,
    }

    if request_id:
        record["request_id"] = request_id

    if metadata:
        record["metadata"] = metadata

    try:
        response = supabase.table("api_usage_tracking").insert(record).execute()
        logger.info(
            f"Tracked API usage: user={user_id}, feature={feature_type}, "
            f"tokens={input_tokens}+{output_tokens}, cost={format_cost(cost_cents)}"
        )
        return response.data[0] if response.data else record
    except Exception as e:
        logger.error(f"Failed to track API usage: {e}")
        return record
