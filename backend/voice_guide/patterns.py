"""
Voice Guide Patterns

Defines forbidden patterns, approved closings, and tone corrections
per HenryHQ_voice_guide.md.
"""

import re
from typing import List, Tuple

# Forbidden patterns - these should be flagged or replaced
FORBIDDEN_PATTERNS = {
    # Corporate jargon
    "leverage": "use",
    "synergize": "work together",
    "circle back": "follow up",
    "touch base": "connect",
    "bandwidth": "time",
    "move the needle": "make an impact",
    "low-hanging fruit": "quick wins",
    "paradigm shift": "change",
    "think outside the box": "be creative",
    "deep dive": "detailed look",
    "at the end of the day": "",  # Remove entirely
    "going forward": "",
    "in terms of": "regarding",
    "with regard to": "about",
    "in order to": "to",
    "utilize": "use",
    "facilitate": "help",
    "optimize": "improve",
    "streamline": "simplify",
    "best-in-class": "excellent",

    # Filler words - flag for removal
    "just": "",
    "maybe": "",
    "kind of": "",
    "sort of": "",
    "a bit": "",
    "quite": "",
    "really": "",
    "very": "",
    "actually": "",
    "basically": "",
    "literally": "",

    # Hedging patterns
    "you might want to consider": "consider",
    "perhaps you could": "you should",
    "it might be helpful to": "you should",
    "you may want to": "you should",
    "it could be beneficial": "it would help",

    # Hype patterns
    "amazing": "",
    "incredible": "",
    "awesome": "",
    "fantastic": "",
    "perfect": "",
    "excellent work": "",
    "great job": "",
    "well done": "",
    "you'll crush it": "",
    "you've got this": "",
    "you're going to nail it": "",

    # False encouragement
    "you'll definitely": "you may",
    "for sure": "",
    "no doubt": "",
    "absolutely": "",
    "100%": "",
}

# Patterns that indicate false promises or unearned praise
FALSE_ENCOURAGEMENT_PATTERNS = [
    r"you'll definitely get",
    r"you're going to get",
    r"guaranteed",
    r"no question",
    r"for sure",
    r"without a doubt",
    r"you're amazing",
    r"you're perfect",
    r"flawless",
    r"you've got nothing to worry about",
    r"don't worry about",
]

# Shame/blame patterns to avoid
SHAME_PATTERNS = [
    r"you failed",
    r"you should have",
    r"you need to be better",
    r"the problem is you",
    r"you're not qualified",
    r"you're not good enough",
    r"you don't have what it takes",
    r"you're missing",  # Okay if followed by actionable
]

# Approved closing phrases (supportive but not hype)
APPROVED_CLOSINGS = [
    "This is fixable.",
    "You're close.",
    "Let's strengthen this.",
    "You can close this gap.",
    "This is a quick fix.",
    "You can address this.",
    "This improves your positioning.",
    "This is within reach.",
    "Focus here first.",
    "Start with this.",
]

# Approved supportive phrases
APPROVED_SUPPORT_PHRASES = [
    "You can fix this.",
    "This is addressable.",
    "This is a solvable gap.",
    "You have the foundation.",
    "Your experience supports this.",
    "This builds on your strengths.",
    "This is achievable.",
    "This is a reasonable stretch.",
]

# Tone corrections: (pattern, replacement, context)
TONE_CORRECTIONS: List[Tuple[str, str, str]] = [
    # Over-enthusiasm to calm confidence
    (r"I'm so excited to", "I'll", "enthusiasm"),
    (r"This is amazing because", "This works because", "enthusiasm"),
    (r"Great news!", "Here's the key point:", "enthusiasm"),

    # Passive to active
    (r"It is recommended that you", "You should", "passive"),
    (r"It would be advisable to", "You should", "passive"),
    (r"It might be helpful if you", "Consider", "passive"),

    # Wordy to concise
    (r"In the event that", "If", "verbose"),
    (r"Due to the fact that", "Because", "verbose"),
    (r"At this point in time", "Now", "verbose"),
    (r"In the near future", "Soon", "verbose"),

    # Corporate to human
    (r"Please don't hesitate to", "Feel free to", "corporate"),
    (r"I hope this finds you well", "", "corporate"),
    (r"Kindly", "Please", "corporate"),
    (r"Per our conversation", "As we discussed", "corporate"),
]

# Next step patterns to ensure action-oriented endings
NEXT_STEP_INDICATORS = [
    r"next step",
    r"start by",
    r"begin with",
    r"first,",
    r"do this:",
    r"action:",
    r"your move:",
    r"try this:",
    r"focus on",
    r"prioritize",
    r"update your",
    r"add",
    r"remove",
    r"change",
    r"revise",
    r"rewrite",
]


def has_next_step(text: str) -> bool:
    """Check if text contains a clear next step."""
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in NEXT_STEP_INDICATORS)


def has_forbidden_pattern(text: str) -> List[str]:
    """Check for forbidden patterns in text. Returns list of found patterns."""
    found = []
    text_lower = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in text_lower:
            found.append(pattern)
    return found


def has_false_encouragement(text: str) -> bool:
    """Check for false encouragement patterns."""
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in FALSE_ENCOURAGEMENT_PATTERNS)


def has_shame_language(text: str) -> bool:
    """Check for shame/blame language."""
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in SHAME_PATTERNS)
