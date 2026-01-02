# Resume Leveling System - Implementation Instructions for Claude Code

## Project Overview

Build a resume analysis tool that assesses candidate leveling using three comprehensive frameworks:
1. Technical IC Framework (Engineer I through Distinguished Engineer)
2. Product Management Framework (APM through VP of Product)
3. Corporate/Non-Technical Framework (10 functions with function-specific title progressions)

The system should analyze resume text and determine:
- Current level based on scope, impact, and competency signals
- Target level the candidate is applying for
- Gap analysis between current and target
- Specific missing competencies or experience
- Resume language quality for target level

## Input Files

You have access to three markdown framework files in `/mnt/user-data/uploads/`:
- `technical_ic_framework.md` - Engineering leveling (Entry → Distinguished)
- `product_management_framework.md` - PM leveling (APM → VP)
- `corporate_framework.md` - 10 corporate functions with title progressions

These files contain:
- Level definitions with scope, impact, and competency descriptions
- Resume language patterns by level
- Progression signals
- Function-specific considerations

## Core Functionality

### 1. Resume Analysis Module

**Input:** Resume text (plain text or parsed from PDF/DOCX)

**Processing:**
- Extract key signals:
  - Years of experience (explicit and implied from dates)
  - Job titles and progression
  - Scope indicators (team size, budget, users, revenue impact)
  - Language patterns (action verbs, impact statements)
  - Technical depth or domain expertise
  - Cross-functional influence
  - Strategic thinking indicators
  - Leadership and mentorship

**Output:** Structured assessment object containing:
```python
{
    "detected_function": str,  # "Engineering", "Product Management", "Legal", etc.
    "current_level": str,  # e.g., "Senior Engineer", "Product Manager"
    "current_level_confidence": float,  # 0-1 score
    "years_experience": int,
    "key_signals": {
        "scope_indicators": [...],
        "impact_statements": [...],
        "technical_depth": [...],
        "leadership_signals": [...],
        "strategic_thinking": [...]
    },
    "language_quality": str,  # "Entry-level", "Mid-level", "Senior-level", etc.
    "notable_achievements": [...],
    "red_flags": [...]  # Generic claims, missing quantification, etc.
}
```

### 2. Level Mapping Module

**Input:** Assessment object + target job title/description

**Processing:**
- Map target title to framework level
- Compare current vs target level
- Identify competency gaps using framework definitions
- Analyze if resume language matches target level

**Output:** Gap analysis object:
```python
{
    "target_level": str,
    "target_level_requirements": {
        "scope": str,
        "impact": str,
        "key_competencies": [...]
    },
    "current_vs_target": {
        "levels_apart": int,  # 0 = matches, 1 = one level below, etc.
        "is_qualified": bool,
        "confidence": float
    },
    "gaps": {
        "scope_gaps": [...],
        "impact_gaps": [...],
        "competency_gaps": [...],
        "language_gaps": [...]
    },
    "strengths": [...],  # What they do have for target level
    "recommendations": [...]  # Specific resume improvements
}
```

### 3. Framework Query Module

**Input:** Function name + level name

**Processing:**
- Load appropriate framework markdown file
- Parse and extract level definition
- Return structured competency data

**Output:** Level definition object:
```python
{
    "function": str,
    "level": str,
    "typical_experience": str,
    "scope": str,
    "impact": str,
    "competencies": {
        "domain_expertise": str,
        "strategic_thinking": str,
        "execution": str,
        "collaboration": str,
        "leadership": str
    },
    "common_titles": [...],  # Alternative titles at this level
    "key_signals": [...],  # What to look for in resumes
    "language_patterns": [...]  # Typical action verbs and phrasing
}
```

## Technical Architecture

### Suggested Tech Stack
- **Language:** Python 3.11+
- **NLP:** spaCy for entity extraction, keyword analysis
- **PDF/DOCX Parsing:** pypdf2, python-docx
- **Framework Storage:** Parse markdown files into structured JSON on startup
- **Matching Logic:** Rule-based + keyword matching (no ML needed for v1)

### Key Components

**1. FrameworkLoader**
```python
class FrameworkLoader:
    """Loads and parses leveling framework markdown files"""
    
    def load_framework(self, function: str) -> Dict:
        """Load framework for specific function"""
        pass
    
    def get_level_definition(self, function: str, level: str) -> Dict:
        """Get detailed level definition"""
        pass
    
    def get_all_levels(self, function: str) -> List[str]:
        """Get ordered list of levels for function"""
        pass
    
    def map_title_to_level(self, function: str, title: str) -> str:
        """Map job title to framework level"""
        pass
```

**2. ResumeParser**
```python
class ResumeParser:
    """Parses resume and extracts structured information"""
    
    def parse_text(self, resume_text: str) -> Dict:
        """Extract structured data from resume text"""
        pass
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience with dates, titles, companies"""
        pass
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        pass
    
    def calculate_years_experience(self, experiences: List[Dict]) -> int:
        """Calculate total years of experience"""
        pass
```

**3. SignalExtractor**
```python
class SignalExtractor:
    """Extracts leveling signals from resume"""
    
    def extract_scope_indicators(self, text: str) -> List[str]:
        """
        Extract scope signals:
        - Team size mentions ("led team of 5", "managed 12 engineers")
        - Budget size ("$2M budget", "managed $500K spend")
        - User scale ("10M users", "enterprise customers")
        - Geographic scope ("global", "3 regions", "APAC")
        """
        pass
    
    def extract_impact_statements(self, text: str) -> List[str]:
        """
        Extract impact signals:
        - Metrics with improvements ("increased X by 30%")
        - Revenue impact ("drove $5M in revenue")
        - Efficiency gains ("reduced time by 40%")
        - Business outcomes ("launched product used by 1M users")
        """
        pass
    
    def extract_action_verbs(self, text: str) -> List[str]:
        """Extract action verbs and categorize by level"""
        pass
    
    def extract_leadership_signals(self, text: str) -> List[str]:
        """
        Extract leadership signals:
        - "mentored", "coached", "developed"
        - "led", "managed", "directed"
        - "hired", "built team"
        - "influenced", "drove alignment"
        """
        pass
    
    def extract_strategic_signals(self, text: str) -> List[str]:
        """
        Extract strategic thinking signals:
        - "strategy", "vision", "roadmap"
        - "defined", "shaped", "established"
        - Cross-org work ("partnered with", "aligned with")
        """
        pass
    
    def detect_function(self, text: str, titles: List[str]) -> str:
        """
        Detect primary function from resume
        Look at job titles, skills, experience descriptions
        """
        pass
```

**4. LevelAnalyzer**
```python
class LevelAnalyzer:
    """Analyzes resume against framework to determine level"""
    
    def __init__(self, framework_loader: FrameworkLoader):
        self.frameworks = framework_loader
    
    def assess_current_level(
        self, 
        signals: Dict, 
        function: str,
        titles: List[str]
    ) -> Dict:
        """
        Determine current level based on:
        - Title progression
        - Years of experience
        - Scope signals
        - Impact signals
        - Language patterns
        - Competency signals
        """
        pass
    
    def compare_to_target(
        self,
        current_assessment: Dict,
        target_level: str,
        function: str
    ) -> Dict:
        """
        Compare current level to target level
        Identify specific gaps
        """
        pass
    
    def generate_recommendations(
        self,
        gap_analysis: Dict,
        function: str
    ) -> List[str]:
        """
        Generate specific, actionable recommendations
        to strengthen resume for target level
        """
        pass
```

**5. LanguageAnalyzer**
```python
class LanguageAnalyzer:
    """Analyzes resume language quality for target level"""
    
    def assess_language_level(self, text: str, experiences: List[Dict]) -> str:
        """
        Classify resume language as:
        - Entry-level: "Assisted", "Supported", "Helped"
        - Mid-level: "Managed", "Led", "Built", "Developed"
        - Senior-level: "Drove", "Established", "Architected"
        - Principal-level: "Defined", "Pioneered", "Transformed"
        """
        pass
    
    def check_quantification(self, text: str) -> Dict:
        """
        Check for quantified impact statements
        Return % of statements with numbers/metrics
        """
        pass
    
    def detect_red_flags(self, text: str) -> List[str]:
        """
        Detect problematic patterns:
        - Generic buzzwords without substance
        - Passive voice
        - Vague claims ("various", "several", "multiple")
        - Missing metrics at senior levels
        - Over-claiming (junior title with principal-level claims)
        """
        pass
    
    def suggest_language_improvements(
        self,
        current_language: str,
        target_level: str,
        function: str
    ) -> List[str]:
        """Generate specific language improvement suggestions"""
        pass
```

## Matching Logic Guidelines

### Function Detection
```python
function_keywords = {
    "Engineering": [
        "software engineer", "engineer", "developer", "sre", "devops",
        "backend", "frontend", "full stack", "ml engineer", "data engineer",
        "coding", "programming", "architecture", "system design"
    ],
    "Product Management": [
        "product manager", "product owner", "apm", "pm",
        "product strategy", "roadmap", "product vision", "user stories"
    ],
    "Legal": [
        "attorney", "lawyer", "counsel", "legal", "general counsel",
        "bar admission", "j.d.", "law"
    ],
    # ... etc for all functions
}
```

### Level Detection Heuristics

**For Technical IC:**
```python
def assess_engineering_level(signals, years_exp, titles):
    # Title-based signals
    if any(title in ["Engineer I", "Junior Engineer", "Software Engineer I"] for title in titles):
        level = "Engineer I"
    elif any(title in ["Senior", "Sr.", "Staff", "Principal"] for title in titles):
        # Need to distinguish Senior/Staff/Principal
        if "Principal" in titles or "Distinguished" in titles:
            level = "Principal Engineer"
        elif "Staff" in titles:
            if "Senior Staff" in titles:
                level = "Senior Staff Engineer"
            else:
                level = "Staff Engineer"
        else:
            level = "Senior Engineer"
    else:
        level = "Engineer II"
    
    # Validate with scope/impact signals
    if level == "Staff Engineer":
        required_signals = [
            "multi-team impact",
            "technical leadership",
            "defined standards/architecture",
            "8+ years experience"
        ]
        # Check if signals support this level
    
    return level
```

**Scope Indicators by Level:**
```python
scope_patterns = {
    "Entry (Engineer I, APM, Associate)": [
        r"small (?:team|feature|component)",
        r"assigned (?:tasks|projects)",
        r"under (?:direction|guidance|supervision)",
        r"supported .+ team"
    ],
    "Mid (Engineer II, PM, Specialist)": [
        r"(?:owned|managed|led) (?:feature|project|workstream)",
        r"independently (?:delivered|executed|managed)",
        r"team of (\d+)",  # Small teams (1-3)
    ],
    "Senior (Senior Engineer, Senior PM)": [
        r"cross-team",
        r"(?:multiple|several) (?:teams|projects|features)",
        r"mentored \d+ (?:engineers|team members)",
        r"team of ([4-9]|\d{2})",  # Larger teams
        r"defined strategy",
        r"technical lead"
    ],
    "Staff/Lead": [
        r"organization(?:al)?-wide",
        r"company-wide",
        r"multiple (?:teams|organizations|groups)",
        r"(?:defined|established|created) (?:standards|frameworks|architecture)",
        r"(\d+)\+ (?:engineers|team members)"  # 10+
    ]
    # ... etc
}
```

**Impact Indicators by Level:**
```python
impact_patterns = {
    "Entry": [
        r"contributed to",
        r"supported .+ that (?:resulted|led)",
        r"helped (?:improve|achieve)"
    ],
    "Mid": [
        r"(?:improved|increased|reduced) .+ by (\d+)%",
        r"(?:delivered|shipped|launched) .+ used by (\d+)",
        r"saved \$(\d+)"
    ],
    "Senior": [
        r"drove \$(\d+[MK]) (?:in )?revenue",
        r"(?:increased|improved) .+ by (\d+)% (?:across|for) .+ (?:teams|organization)",
        r"enabled .+ to (?:scale|grow)"
    ],
    "Staff/Principal": [
        r"transformed",
        r"company-wide impact",
        r"business-critical",
        r"(?:defined|shaped) (?:company|organization) strategy"
    ]
}
```

### Title Normalization

```python
def normalize_title(title: str) -> str:
    """
    Normalize variations:
    - "Sr. Engineer" → "Senior Engineer"
    - "SWE II" → "Software Engineer II"
    - "Prin. PM" → "Principal Product Manager"
    """
    pass

# Title equivalence mappings
title_mappings = {
    "Engineering": {
        "Software Engineer I": ["Engineer I", "SWE I", "Junior Engineer"],
        "Software Engineer II": ["Engineer II", "SWE II", "Software Engineer"],
        "Senior Engineer": ["Sr. Engineer", "Senior SWE", "SWE III"],
        "Staff Engineer": ["Staff SWE"],
        # ... etc
    },
    "Product Management": {
        "Associate Product Manager": ["APM", "Associate PM"],
        "Product Manager": ["PM", "Product Manager I"],
        # ... etc
    }
    # ... etc
}
```

## Output Format

### Console Output for Analysis

```
=== Resume Leveling Analysis ===

Function Detected: Engineering
Current Level: Senior Engineer (Confidence: 85%)
Years of Experience: 7 years

--- Current Level Assessment ---

Key Strengths:
✓ Clear cross-team impact and influence
✓ Technical leadership demonstrated (architected X, defined Y)
✓ Mentorship of junior engineers
✓ Quantified impact on system reliability (99.9% to 99.99%)
✓ Appropriate language for Senior level

Scope Indicators Found:
- Led team of 5 engineers
- Cross-functional collaboration with Product, Design teams
- Owned authentication service used by 10M users

Impact Statements Found:
- Reduced API latency by 40%
- Improved system reliability from 99.9% to 99.99%
- Saved $500K/year in infrastructure costs

--- Target Level Analysis ---

Target: Staff Engineer

Gap Analysis:
✗ Missing: Evidence of multi-team or org-wide technical leadership
✗ Missing: Framework/standard definition that scaled beyond immediate team
✗ Missing: External visibility (conference talks, blog posts, open source)
⚠ Weak: Strategic thinking signals (mostly execution-focused)
✓ Strong: Technical depth appears sufficient

Recommendations:
1. Add examples of work that influenced multiple teams
2. Highlight any frameworks, tools, or standards you created that others adopted
3. Emphasize strategic technical decisions with business impact
4. Include any technical leadership outside your immediate team (mentoring, design reviews)
5. Strengthen language: Use "defined", "established", "drove adoption" vs "built", "implemented"

Language Quality: Appropriate for Senior level, needs elevation for Staff level
- Current: 70% execution-focused verbs (built, implemented, developed)
- Target: 50%+ strategic/leadership verbs (defined, established, architected)

=== End Analysis ===
```

### Structured JSON Output

```json
{
  "analysis_version": "1.0",
  "timestamp": "2025-12-11T23:45:00Z",
  "resume_info": {
    "total_years_experience": 7,
    "num_positions": 4,
    "education_level": "Bachelor's"
  },
  "function_detection": {
    "primary_function": "Engineering",
    "confidence": 0.92,
    "secondary_functions": []
  },
  "current_level": {
    "level": "Senior Engineer",
    "confidence": 0.85,
    "supporting_evidence": [
      "7 years of experience",
      "Cross-team technical leadership",
      "Mentorship demonstrated",
      "Appropriate scope for Senior level"
    ],
    "contradicting_evidence": [
      "Title at most recent company was 'Software Engineer II'"
    ]
  },
  "signals": {
    "scope": [
      "Led team of 5 engineers",
      "Owned authentication service (10M users)",
      "Cross-functional collaboration"
    ],
    "impact": [
      "Reduced API latency by 40%",
      "Improved reliability 99.9% → 99.99%",
      "Saved $500K/year infrastructure costs"
    ],
    "technical_depth": [
      "Distributed systems expertise",
      "Designed and implemented microservices architecture",
      "Performance optimization"
    ],
    "leadership": [
      "Mentored 3 junior engineers",
      "Led technical design reviews",
      "Drove adoption of testing standards"
    ],
    "strategic_thinking": [
      "Evaluated build vs buy for auth system",
      "Proposed and implemented caching strategy"
    ]
  },
  "language_analysis": {
    "level": "Senior-level",
    "action_verb_distribution": {
      "entry_level": 0.05,
      "mid_level": 0.25,
      "senior_level": 0.60,
      "principal_level": 0.10
    },
    "quantification_rate": 0.65,
    "red_flags": [
      "Some generic claims without specifics ('various projects')"
    ]
  },
  "target_analysis": {
    "target_level": "Staff Engineer",
    "levels_apart": 1,
    "is_qualified": false,
    "confidence": 0.45,
    "gaps": {
      "scope_gaps": [
        "Multi-team/org-wide technical leadership",
        "Framework or standard definition beyond immediate team"
      ],
      "impact_gaps": [
        "Business-level (not just team-level) impact",
        "Org-wide system improvements"
      ],
      "competency_gaps": [
        "External visibility (conferences, blog posts, open source)",
        "Company-wide technical strategy influence",
        "Deep expertise in multiple domains (currently 1-2)"
      ],
      "language_gaps": [
        "Need more strategic/leadership verbs (defined, established, pioneered)",
        "Too execution-focused (built, implemented, developed)"
      ]
    },
    "strengths": [
      "Technical depth strong for Staff level",
      "Leadership experience demonstrated",
      "Impact quantification good"
    ],
    "recommendations": [
      {
        "type": "content",
        "priority": "high",
        "recommendation": "Add examples of work that influenced multiple teams beyond your immediate org"
      },
      {
        "type": "content",
        "priority": "high",
        "recommendation": "Highlight any frameworks, tools, or standards you created that others adopted"
      },
      {
        "type": "language",
        "priority": "medium",
        "recommendation": "Replace 'built' with 'architected' or 'designed' where appropriate"
      },
      {
        "type": "language",
        "priority": "medium",
        "recommendation": "Replace 'implemented' with 'drove adoption of' or 'established' where appropriate"
      },
      {
        "type": "content",
        "priority": "medium",
        "recommendation": "Add any external visibility: conference talks, blog posts, open source contributions"
      }
    ]
  }
}
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- Framework loader (parse markdown files)
- Basic resume parser (text extraction)
- Function detection
- Title normalization

### Phase 2: Signal Extraction (Week 1-2)
- Scope indicator extraction
- Impact statement extraction
- Action verb analysis
- Leadership signal detection
- Strategic thinking indicators

### Phase 3: Level Assessment (Week 2)
- Current level determination
- Confidence scoring
- Evidence collection
- Red flag detection

### Phase 4: Gap Analysis (Week 2-3)
- Target level requirements loading
- Gap identification
- Recommendation generation
- Language analysis

### Phase 5: Output & UX (Week 3)
- Console output formatting
- JSON export
- Web interface (optional)
- Batch processing support

### Phase 6: Refinement (Week 3-4)
- Calibration against real resumes
- Edge case handling
- Performance optimization
- Documentation

## Testing Strategy

### Unit Tests
- Framework parsing accuracy
- Signal extraction precision
- Level mapping correctness
- Title normalization

### Integration Tests
- End-to-end resume analysis
- Gap analysis accuracy
- Recommendation quality

### Validation Dataset
Create test set of 20-30 resumes across:
- Engineering (5-7 resumes at different levels)
- Product Management (3-5 resumes)
- Corporate functions (10-15 resumes across functions)

For each test resume:
- Known actual level
- Known target level
- Expected gaps
- Expected recommendations

### Success Metrics
- Function detection accuracy: >90%
- Level detection accuracy (±1 level): >80%
- Gap identification completeness: Subjective review
- Recommendation usefulness: Subjective review

## Configuration & Customization

### Config File (config.yaml)
```yaml
frameworks:
  technical_ic: /mnt/user-data/uploads/technical_ic_framework.md
  product_management: /mnt/user-data/uploads/product_management_framework.md
  corporate: /mnt/user-data/uploads/corporate_framework.md

confidence_thresholds:
  function_detection: 0.70
  level_assessment: 0.60
  qualification_decision: 0.70

weights:
  title_based: 0.30
  scope_signals: 0.25
  impact_signals: 0.25
  language_patterns: 0.10
  years_experience: 0.10

output:
  format: both  # 'console', 'json', or 'both'
  json_output_path: ./analysis_output.json
  verbosity: detailed  # 'minimal', 'standard', 'detailed'
```

## Edge Cases to Handle

1. **Career Changers**: 10 years experience but switching from finance to engineering
   - Discount years for function change
   - Look for transferable signals

2. **Title Inflation**: "VP" at 5-person startup vs 5000-person company
   - Check scope signals heavily
   - Compare against framework not just title

3. **Ambiguous Titles**: "Manager" could be IC or people manager
   - Look for team size mentions
   - Check for hiring/performance management language

4. **Multiple Functions**: Did sales, then product, then strategy
   - Detect primary function based on most recent/longest tenure
   - Note function switches in analysis

5. **Missing Information**: Resume light on quantification or scope
   - Flag as "insufficient information to assess"
   - Provide lower confidence scores
   - Suggest what's needed

6. **Over-claiming**: Junior title but principal-level language
   - Flag as red flag
   - Note inconsistency between title and claims
   - Assess conservatively

7. **International Titles**: Different conventions in Europe/Asia
   - Build international title mappings
   - Note when assumptions made

## Success Criteria for v1

The system should be able to:

✓ Correctly identify function for 90% of clear resumes
✓ Assess current level within ±1 level for 80% of cases
✓ Identify major gaps when candidate is 2+ levels below target
✓ Generate 3-5 actionable, specific recommendations per resume
✓ Flag obvious red flags (generic claims, missing quantification)
✓ Process a resume in <10 seconds
✓ Output both human-readable and machine-readable formats

## Next Steps After v1

Potential enhancements:
- ML model for more nuanced level detection
- Resume rewriting suggestions (specific before/after)
- Competitive intelligence (how does this compare to market?)
- Interview question generation based on level and gaps
- Integration with ATS systems
- Chrome extension for LinkedIn profile analysis
- API for integration with HenryAI

## File Structure

```
resume-leveling-system/
├── README.md
├── requirements.txt
├── config.yaml
├── src/
│   ├── __init__.py
│   ├── framework_loader.py
│   ├── resume_parser.py
│   ├── signal_extractor.py
│   ├── level_analyzer.py
│   ├── language_analyzer.py
│   ├── gap_analyzer.py
│   └── output_formatter.py
├── frameworks/
│   ├── technical_ic_framework.md
│   ├── product_management_framework.md
│   └── corporate_framework.md
├── tests/
│   ├── test_framework_loader.py
│   ├── test_signal_extraction.py
│   ├── test_level_analysis.py
│   └── test_data/
│       └── sample_resumes/
├── data/
│   ├── function_keywords.json
│   ├── title_mappings.json
│   ├── scope_patterns.json
│   └── impact_patterns.json
└── main.py
```

---

## New Backend Modules (January 2026)

The following modules were added to support the Document Quality & Trust Layer:

### 1. canonical_document.py (~770 lines)

**Purpose:** Single source of truth for preview and download. Eliminates P0 bug where preview ≠ download.

**Key Classes:**
```python
@dataclass
class CanonicalContact:
    """Contact information for document header."""
    name: str
    email: str
    phone: str
    location: str
    linkedin: str

@dataclass
class CanonicalExperience:
    """Single work experience entry."""
    title: str
    company: str
    dates: str
    bullets: List[str]

@dataclass
class CanonicalResume:
    """Complete resume ready for preview/download."""
    contact: CanonicalContact
    tagline: str
    summary: str
    experience: List[CanonicalExperience]
    education: List[Dict[str, Any]]
    skills: List[str]
    competencies: List[str]
    full_text: str  # Pre-rendered for preview

@dataclass
class FitScoreDelta:
    """Tracks fit score improvement from original to canonical."""
    original_score: int
    final_score: int
    original_verdict: str
    final_verdict: str
    improvement_summary: str
    score_locked: bool = False
    locked_at: Optional[str] = None

@dataclass
class CanonicalDocument:
    """The complete canonical document object - ONLY source for preview and download."""
    resume: CanonicalResume
    cover_letter: CanonicalCoverLetter
    metadata: DocumentMetadata
```

**Key Functions:**
```python
def check_document_integrity(doc: CanonicalDocument) -> Dict[str, Any]:
    """Validates document before download - checks contact info, keyword frequency."""

def deduplicate_keywords(text: str, max_occurrences: int = 3) -> str:
    """Caps keyword frequency at max_occurrences to prevent stuffing."""

def calculate_fit_score_delta(original_score, original_verdict, canonical_resume, jd_keywords) -> FitScoreDelta:
    """Calculate delta using SAME scoring logic as initial analysis."""

def assemble_canonical_document(generation_output, source_resume, job_description, contact_info, ...) -> CanonicalDocument:
    """Single assembly point - no reconstruction allowed after this."""
```

### 2. strengthen_session.py (~470 lines)

**Purpose:** Manage strengthen flow sessions with constrained user inputs and audit trail.

**Key Classes:**
```python
@dataclass
class BulletRegeneration:
    """Tracks each regeneration attempt."""
    original_bullet: str
    issue_type: str  # "missing_metrics", "vague_ownership", etc.
    user_inputs: Dict[str, str]
    generated_bullet: str
    generation_number: int  # 1, 2, or 3 (max)
    accepted: bool
    timestamp: datetime

@dataclass
class StrengthenSession:
    """Complete session state."""
    session_id: str
    resume_id: str
    issues_found: List[str]
    issues_addressed: List[str]
    issues_skipped: List[str]
    regenerations: List[BulletRegeneration]
    started_at: datetime
    completed_at: Optional[datetime]
```

**Validation Rules:**
```python
FORBIDDEN_PATTERNS = [
    r"I also (did|led|managed|created)",  # New accomplishments
    r"promoted to|became|was made",        # Title changes
    r"learned|picked up|started using",    # New skills
    r"worked at|joined|started at",        # New companies
]

IMPLAUSIBLE_THRESHOLDS = {
    "revenue_impact_entry_level": 1_000_000,      # $1M+ for entry suspicious
    "team_size_ic": 50,                           # 50+ direct reports for IC suspicious
    "percentage_improvement": 500,                 # 500%+ improvement suspicious
}

def validate_user_input(user_input: str, context: Dict) -> Tuple[bool, Optional[str]]:
    """Validates against forbidden patterns and implausible thresholds."""
```

### 3. resume_detection.py (~760 lines)

**Purpose:** Detection systems for credibility, title inflation, and career switcher patterns.

**Key Functions:**
```python
def assess_company_credibility(company: str, role: Dict) -> Dict[str, Any]:
    """
    Returns:
    {
        "status": "Strong" | "Weak" | "Unverifiable",
        "explanation": str,
        "multiplier": float  # 1.0, 0.7, 0.3, or 0
    }
    """

def detect_title_inflation(experience: List[Dict]) -> Dict[str, Any]:
    """
    Returns:
    {
        "detected": bool,
        "evidence_level": "Aligned" | "Inflated" | "Undersold",
        "supporting_analysis": str
    }
    """

def recognize_career_switcher(experience: List[Dict], target_function: str) -> Dict[str, Any]:
    """
    Returns:
    {
        "is_switcher": bool,
        "experience_type": "Direct" | "Adjacent" | "Exposure",
        "transferability": str
    }
    """
```

### 4. resume_language_lint.py (~440 lines)

**Purpose:** Detect and flag mid-market language that weakens senior signal.

**Pattern Tiers:**
```python
TIER_1_PATTERNS = [  # Kill on sight - remove entirely
    (r"\bresults-driven\b", "Says nothing, universal filler", "Delete entirely"),
    (r"\bpassionate about\b", "Emotion, not evidence", "Delete"),
    (r"\bteam player\b", "Table stakes, not differentiator", "Delete"),
    ...
]

TIER_2_PATTERNS = [  # Passive/junior-coded - rewrite
    (r"\bresponsible for\b", "Passive, job description language", "'Owned [X]' or 'Led [X]'"),
    (r"\bhelped? (?:drive|build|create)\b", "Who owned the decision?", "'Drove [X]'"),
    ...
]

TIER_3_PATTERNS = [  # Vague scope hiders - replace with specifics
    (r"\bvarious stakeholders\b", "Hides level, could be anyone", "Name the levels"),
    (r"\bmultiple teams\b", "How many? What scope?", "'4 engineering teams (35 engineers)'"),
    ...
]

TIER_4_PATTERNS = [  # Exposure without ownership
    (r"\bexposure to\b", "Observer, not operator", "Remove or show what you did"),
    (r"\bfamiliar with\b", "Learning, not doing", "Remove or upgrade"),
    ...
]
```

**Key Functions:**
```python
def fails_linkedin_test(sentence: str) -> Tuple[bool, List[str]]:
    """If sentence could appear on 1,000+ LinkedIn profiles unchanged, it fails."""

def fails_ownership_test(sentence: str) -> Tuple[bool, List[str]]:
    """If sentence doesn't answer 'what broke if you weren't there?', it fails."""

def lint_resume(resume: Dict[str, Any]) -> Dict[str, Any]:
    """Complete lint with structured results for API response."""

def auto_rewrite_bullet(bullet: str) -> Tuple[str, List[str]]:
    """Apply automatic rewrites for Tier 1/2 patterns."""
```

### 5. resume_quality_gates.py (~790 lines)

**Purpose:** Pre-submission validation to catch issues before download.

**Gate System:**
```python
def check_contact_info_gate(document: Dict) -> Dict[str, Any]:
    """Validates contact info is present and complete."""

def check_keyword_frequency_gate(document: Dict, max_per_keyword: int = 3) -> Dict[str, Any]:
    """Validates no keyword stuffing."""

def check_quantification_gate(document: Dict, min_rate: float = 0.3) -> Dict[str, Any]:
    """Validates sufficient metrics in bullets."""

def check_bullet_length_gate(document: Dict) -> Dict[str, Any]:
    """Validates bullet length (not too short, not too long)."""

def run_all_gates(document: Dict) -> Dict[str, Any]:
    """Run all gates and return aggregate result with pass/fail and issues."""
```

### 6. document_versioning.py (~600 lines)

**Purpose:** Track document versions for audit trail and comparison.

**Key Classes:**
```python
@dataclass
class DocumentVersion:
    """Single version of a document."""
    version_id: str
    document_type: str  # "resume" | "cover_letter"
    content_hash: str
    created_at: datetime
    changes_from_previous: List[str]
    user_approved: bool

@dataclass
class VersionHistory:
    """Complete version history for a document."""
    document_id: str
    versions: List[DocumentVersion]
    current_version_id: str
```

---

## API Endpoints Added (January 2026)

### Strengthen Flow Endpoints

```
POST /api/strengthen/session
  - Creates a new strengthen session
  - Returns: session_id, issues_list, priority_order

GET /api/strengthen/session/{session_id}
  - Gets current session state
  - Returns: issues, progress, regenerations

POST /api/strengthen/regenerate
  - Generates strengthened bullet
  - Body: { session_id, issue_id, user_inputs }
  - Returns: { original, strengthened, changes, generation_number }
  - Validates user inputs against forbidden patterns

POST /api/strengthen/accept
  - Accepts a regenerated bullet
  - Body: { session_id, issue_id, regeneration_id }

POST /api/strengthen/skip
  - Skips an issue
  - Body: { session_id, issue_id, reason? }

POST /api/strengthen/complete
  - Marks session complete
  - Returns: { summary, before_after_comparison }
```

### Canonical Download Endpoint

```
GET /api/download/canonical
  - Downloads canonical document (resume or cover letter)
  - Uses stored canonical document (no reassembly)
  - Runs integrity checks before download
  - Returns: File stream with proper headers
```

---

## Frontend Integration (January 2026)

### documents.html Changes

```javascript
// Preview uses canonical_full_text (pre-rendered)
function renderPreview(canonicalDoc) {
    previewContainer.innerHTML = canonicalDoc.resume.full_text;
}

// Download uses canonical endpoint
async function downloadDocument(type) {
    const response = await fetch('/api/download/canonical', {
        method: 'POST',
        body: JSON.stringify({ document_type: type, session_id: currentSessionId })
    });
    // Stream file to download
}

// Fit Score Delta display
function showFitScoreDelta(delta) {
    if (!delta.improved && delta.delta === 0) {
        // Show honest message
        statusText.textContent = delta.improvement_summary;
    } else {
        // Show improvement
        statusText.textContent = `+${delta.delta} points: ${delta.improvement_summary}`;
    }
}

// Lock score at download
function lockFitScoreAtDownload() {
    // Called on "Approve & Download" click
    // Prevents gamification
}
```

### resume-leveling.html Changes

```javascript
// Credibility & Verifiability section
function renderCredibility(data) {
    // Company Credibility cards
    renderCompanyCards(data.company_credibility);

    // Title Alignment cards
    renderTitleCards(data.title_alignment);

    // Experience Relevance cards (for career switchers)
    if (data.is_career_switcher) {
        renderExperienceCards(data.experience_relevance);
    }
}
```

## Sample Usage

```python
# Simple API
from resume_leveling import ResumeLeveler

leveler = ResumeLeveler(config_path="config.yaml")

# Analyze a resume
with open("resume.txt") as f:
    resume_text = f.read()

result = leveler.analyze(
    resume_text=resume_text,
    target_title="Staff Engineer"  # Optional
)

# Get console output
result.print_summary()

# Get JSON
json_output = result.to_json()

# Get specific sections
print(f"Current Level: {result.current_level}")
print(f"Confidence: {result.confidence}")
print(f"Key Gaps: {result.gaps}")
print(f"Recommendations: {result.recommendations}")

# Batch processing
resumes = load_resume_folder("./resumes/")
results = leveler.analyze_batch(resumes, target_title="Senior Engineer")
results.export_csv("analysis_results.csv")
```

## Questions for Clarification

Before starting implementation, confirm:

1. **Primary use case**: Is this for your internal recruiting workflow, or a product you'll offer to others?
2. **Volume**: How many resumes need to be processed? (affects architecture decisions)
3. **Integration**: Does this need to integrate with existing ATS or will it be standalone?
4. **UI requirements**: CLI only, web interface, or API?
5. **Accuracy requirements**: Is 80% good enough or do you need 95%+?
6. **Real-time vs batch**: Immediate results or overnight batch processing okay?

## Starting Point

For Claude Code implementation:

1. Start with framework loading - parse the three markdown files
2. Build basic resume parser - extract text, find titles and dates
3. Implement function detection - keyword matching against frameworks
4. Add scope/impact signal extraction with regex patterns
5. Build level assessment with simple rule-based logic
6. Add gap analysis by comparing current vs target
7. Format output for console and JSON
8. Test against sample resumes
9. Iterate and refine based on results

The frameworks you've built are the "brain" of this system. The code is just plumbing to extract signals from resumes and match them against your frameworks. Keep the logic simple and transparent - it's better to have clear rules you can debug than a black box that sometimes works.
