"""
Reality Check System - HenryHQ's market-truth intervention framework.

This module implements the Reality Check System as specified in REALITY_CHECK_SPEC.md.
It surfaces risk, friction, and market behavior patterns early enough for candidates
to make informed strategic decisions.

Core Principle: Transparency over false hope. Strategy over suppression.

Signal Classes:
1. Eligibility Signals - Hard requirements (Blocker only)
2. Fit Signals - Experience matching (Warning, Coaching)
3. Credibility Signals - Claim believability (Warning, Coaching)
4. Risk Signals - Pattern recognition (Warning, Coaching)
5. Market Bias Signals - Hiring preferences (Coaching only, NEVER modifies score)
6. Market Climate Signals - External conditions (Informational only, NEVER modifies score)
"""

from .reality_check_controller import RealityCheckController, analyze_reality_checks
from .signal_detectors import (
    detect_eligibility_signals,
    detect_fit_signals,
    detect_credibility_signals,
    detect_risk_signals,
    detect_market_bias_signals,
    detect_market_climate_signals,
    detect_company_health_signals,
)
from .models import (
    RealityCheck,
    SignalClass,
    Severity,
    FORBIDDEN_INTERACTIONS,
)

__all__ = [
    'RealityCheckController',
    'analyze_reality_checks',
    'detect_eligibility_signals',
    'detect_fit_signals',
    'detect_credibility_signals',
    'detect_risk_signals',
    'detect_market_bias_signals',
    'detect_market_climate_signals',
    'detect_company_health_signals',
    'RealityCheck',
    'SignalClass',
    'Severity',
    'FORBIDDEN_INTERACTIONS',
]
