"""
Anthropic API Pricing Configuration

Pricing is stored in cents per million tokens for precision.
Last updated: January 2025
"""

# Pricing in cents per million tokens
# This makes calculations easier and avoids floating point issues
ANTHROPIC_PRICING = {
    # Claude Sonnet 4 (current default)
    "claude-sonnet-4-20250514": {
        "input_cents_per_million": 300,   # $3.00 per million input tokens
        "output_cents_per_million": 1500,  # $15.00 per million output tokens
    },
    # Claude 3.5 Sonnet (legacy)
    "claude-3-5-sonnet-20241022": {
        "input_cents_per_million": 300,
        "output_cents_per_million": 1500,
    },
    # Claude 3.5 Haiku
    "claude-3-5-haiku-20241022": {
        "input_cents_per_million": 100,   # $1.00 per million input tokens
        "output_cents_per_million": 500,   # $5.00 per million output tokens
    },
    # Claude 3 Opus
    "claude-3-opus-20240229": {
        "input_cents_per_million": 1500,  # $15.00 per million input tokens
        "output_cents_per_million": 7500,  # $75.00 per million output tokens
    },
}

# Default model used by the application
DEFAULT_MODEL = "claude-sonnet-4-20250514"


def calculate_cost_cents(model: str, input_tokens: int, output_tokens: int) -> int:
    """
    Calculate the cost in cents for an API call.

    Args:
        model: The model ID used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in cents (integer)
    """
    pricing = ANTHROPIC_PRICING.get(model, ANTHROPIC_PRICING[DEFAULT_MODEL])

    # Calculate cost: (tokens / 1_000_000) * cents_per_million
    input_cost = (input_tokens * pricing["input_cents_per_million"]) / 1_000_000
    output_cost = (output_tokens * pricing["output_cents_per_million"]) / 1_000_000

    # Round to nearest cent
    total_cents = round(input_cost + output_cost)

    return total_cents


def format_cost(cost_cents: int) -> str:
    """
    Format cost in cents to a human-readable string.

    Args:
        cost_cents: Cost in cents

    Returns:
        Formatted string like "$0.05" or "$1.23"
    """
    dollars = cost_cents / 100
    return f"${dollars:.2f}"


def get_model_pricing_info(model: str) -> dict:
    """
    Get pricing information for a model.

    Args:
        model: The model ID

    Returns:
        Dict with input_per_million and output_per_million in dollars
    """
    pricing = ANTHROPIC_PRICING.get(model, ANTHROPIC_PRICING[DEFAULT_MODEL])
    return {
        "model": model,
        "input_per_million_tokens": f"${pricing['input_cents_per_million'] / 100:.2f}",
        "output_per_million_tokens": f"${pricing['output_cents_per_million'] / 100:.2f}",
    }
