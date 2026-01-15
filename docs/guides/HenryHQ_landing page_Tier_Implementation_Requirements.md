# HenryHQ Implementation Requirements
## Phase 1: Landing Page Updates + Phase 2: Tier Logic

---

# PHASE 1: LANDING PAGE UPDATES

## 1.1 Pricing Section

**Location:** After features section, before any testimonials/social proof

**Section Header:**
```
"Choose Your Plan"
"Quality over quantity. Every tier gives you strategic tools to land the right role."
```

**Tier Cards (5 tiers, responsive grid):**

### Sourcer - Free
Tagline: "See how you stack up"

Features (bullets):
- Three applications with tailored resume + cover letter
- Job fit analysis (50/30/20 scoring)
- LinkedIn profile analysis
- Interview debrief analysis
- Core dashboard metrics

CTA Button: "Get Started"

---

### Recruiter - $25/mo
Tagline: "Tailored applications that don't get auto-rejected"

Features (bullets):
- 15 applications per month with tailored documents
- ATS optimization
- Screening questions analysis
- 15 Henry conversations
- Application tracker
- One mock interview per month

CTA Button: "Start Free Trial"

---

### Principal - $69/mo ⭐ MOST POPULAR
Tagline: "The full toolkit for an active search"

Features (bullets):
- 30 applications per month
- Full outreach templates
- Company & role intelligence
- 30 Henry conversations
- Five mock interviews per month
- Salary benchmarking

CTA Button: "Start Free Trial"

Badge: "Most Popular" (visually highlighted)

---

### Partner - $129/mo
Tagline: "Interview coaching and strategic guidance"

Features (bullets):
- Applications based on your strategy
- Document refinement via Henry
- Story Bank for behavioral examples
- Ten mock interviews per month
- Negotiation guidance
- One 30-min live coaching session per month

CTA Button: "Start Free Trial"

---

### Coach - $225/mo
Tagline: "White glove support until you land"

Features (bullets):
- Everything in Partner
- Unlimited mock interviews
- Pattern + signal analysis
- Rejection forensics
- Full negotiation support
- Two 45-min live coaching sessions per month

CTA Button: "Start Free Trial"

Badge: "White Glove" or "Full Support"

---

**Design Notes:**
- Principal tier should be visually highlighted (border, shadow, or background)
- Coach tier should have premium badge
- Mobile: Stack cards vertically with collapsible feature lists
- All prices should show "/mo" clearly
- Consider toggle for monthly/annual (if offering annual discount later)

---

## 1.2 FAQ Section

**Location:** Bottom of page, before footer

**Style:** Accordion (click question to expand answer)

**Questions and Answers:**

---

**Q: What is Job Fit Scoring (50/30/20)?**

A: We evaluate your fit for each role using three weighted factors: 50% Skills Match (do you have the required technical and functional skills), 30% Experience Match (does your work history align with what the role needs), and 20% Scope/Seniority Match (are you at the right level for this role). This reflects how recruiters actually screen candidates during the hiring process.

---

**Q: Who is Henry?**

A: Henry is your strategic career coach built into the platform. From the moment you start your job search, Henry guides you through every stage: analyzing your fit for roles, preparing tailored documents, prepping for interviews, and debriefing afterward. Henry understands how recruiters evaluate candidates and provides honest, actionable guidance rather than generic advice.

---

**Q: Why do you limit the number of applications?**

A: Quality over quantity. Mass-applying to roles where you're not competitive wastes your time and can hurt your credibility with employers who track repeat applicants. Our limits encourage strategic targeting of roles where you can actually compete. The goal is to help you land a job faster, not apply to more jobs.

---

**Q: What does "based on your strategy" mean for applications?**

A: At Partner and Coach tiers, we don't set an arbitrary monthly limit. Instead, we help you determine the right application volume based on your target roles, timeline, and market conditions. Some searches require 10 highly-focused applications; others require 50. Your strategy determines the number, not an artificial cap.

---

**Q: Do you fabricate or exaggerate experience?**

A: Never. Every claim in your tailored documents comes from your actual background. We reposition and emphasize your experience strategically for each role, but we never invent experience, metrics, or accomplishments. Recruiters and hiring managers can spot fabricated content immediately, and it will disqualify you.

---

**Q: What are Live Career Coaching sessions?**

A: One-on-one sessions with a Career Coach to work through your job search strategy, prepare for high-stakes interviews, or navigate offer negotiations. Partner members receive one 30-minute session per month. Coach members receive two 45-minute sessions per month.

---

**Q: Can I upgrade or downgrade my plan?**

A: Yes. You can change your plan at any time. Upgrades take effect immediately with prorated billing. Downgrades take effect at the end of your current billing period.

---

**Q: What if I land a job quickly?**

A: Congratulations! Cancel anytime. We don't lock you into long-term contracts. If you land a role in your first month, cancel before your next billing cycle and you won't be charged again.

---

## 1.3 How It Works Section (Optional but Recommended)

**Location:** After hero section, before features

**Style:** 4-step horizontal visual (icons or illustrations)

**Steps:**

1. **Upload Your Resume**
   Icon: Document/Upload
   Text: "We parse your background and detect your career level"

2. **Paste a Job Description**
   Icon: Clipboard/Target
   Text: "Get instant fit analysis with strengths, gaps, and recommendation"

3. **Generate Tailored Documents**
   Icon: File/Magic wand
   Text: "Resume and cover letter optimized for the specific role"

4. **Prep, Interview, Land**
   Icon: Briefcase/Checkmark
   Text: "Interview prep, mock interviews, debrief, and negotiation support"

---

# PHASE 2: TIER LOGIC

## 2.1 Database Schema Changes

### User Model Additions

```python
# Add to existing User model

tier: str = 'sourcer'  # 'sourcer', 'recruiter', 'principal', 'partner', 'coach'
tier_started_at: datetime = None

# Stripe fields
stripe_customer_id: str = None
stripe_subscription_id: str = None

# Beta user fields
is_beta_user: bool = False
beta_tier_override: str = None  # Overrides tier if set
beta_expires_at: datetime = None  # null = never expires
beta_discount_percent: int = 0  # 0-100, applies after beta expires
```

### Usage Tracking Table (New)

```python
class UsageTracking:
    id: str  # UUID
    user_id: str  # FK to User
    period_start: datetime  # First day of billing period
    period_end: datetime  # Last day of billing period
    
    # Counters
    applications_used: int = 0
    resumes_generated: int = 0
    cover_letters_generated: int = 0
    henry_conversations_used: int = 0
    mock_interviews_used: int = 0
    coaching_sessions_used: int = 0
    
    created_at: datetime
    updated_at: datetime
```

---

## 2.2 Tier Configuration

```python
TIER_PRICES = {
    'sourcer': 0,
    'recruiter': 25,
    'principal': 69,
    'partner': 129,
    'coach': 225,
}

TIER_LIMITS = {
    'sourcer': {
        'applications_per_month': 3,
        'resumes_per_month': 3,
        'cover_letters_per_month': 3,
        'henry_conversations_per_month': 0,
        'mock_interviews_per_month': 0,
        'coaching_sessions_per_month': 0,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': False,
            'outreach_templates': False,
            'application_tracker': False,
            'company_intelligence': False,
            'linkedin_recommendations': False,
            'linkedin_optimization': False,
            'interview_prep_full': False,
            'interview_prep_limited': False,
            'document_refinement': False,
            'story_bank': False,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': False,
            'negotiation_guidance': False,
            'negotiation_full': False,
            'conversation_memory': False,
            'dashboard_full': False,
            'dashboard_insights': False,
            'dashboard_benchmarking': False,
            'application_alerts': False,
            'career_level_assessment': False,
            'live_coaching': False,
        }
    },
    'recruiter': {
        'applications_per_month': 15,
        'resumes_per_month': 15,
        'cover_letters_per_month': 15,
        'henry_conversations_per_month': 15,
        'mock_interviews_per_month': 1,
        'coaching_sessions_per_month': 0,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': 'limited',
            'application_tracker': True,
            'company_intelligence': False,
            'linkedin_recommendations': False,
            'linkedin_optimization': False,
            'interview_prep_full': False,
            'interview_prep_limited': True,
            'document_refinement': False,
            'story_bank': False,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': False,
            'negotiation_guidance': False,
            'negotiation_full': False,
            'conversation_memory': False,
            'dashboard_full': True,
            'dashboard_insights': False,
            'dashboard_benchmarking': False,
            'application_alerts': False,
            'career_level_assessment': False,
            'live_coaching': False,
        }
    },
    'principal': {
        'applications_per_month': 30,
        'resumes_per_month': 30,
        'cover_letters_per_month': 30,
        'henry_conversations_per_month': 30,
        'mock_interviews_per_month': 5,
        'coaching_sessions_per_month': 0,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': True,
            'application_tracker': True,
            'company_intelligence': True,
            'linkedin_recommendations': True,
            'linkedin_optimization': False,
            'interview_prep_full': True,
            'interview_prep_limited': True,
            'document_refinement': False,
            'story_bank': False,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': True,
            'negotiation_guidance': False,
            'negotiation_full': False,
            'conversation_memory': False,
            'dashboard_full': True,
            'dashboard_insights': False,
            'dashboard_benchmarking': False,
            'application_alerts': True,
            'career_level_assessment': False,
            'live_coaching': False,
        }
    },
    'partner': {
        'applications_per_month': -1,  # -1 = unlimited/strategic
        'resumes_per_month': -1,
        'cover_letters_per_month': -1,
        'henry_conversations_per_month': -1,
        'mock_interviews_per_month': 10,
        'coaching_sessions_per_month': 1,
        'coaching_session_minutes': 30,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': True,
            'application_tracker': True,
            'company_intelligence': True,
            'linkedin_recommendations': True,
            'linkedin_optimization': True,
            'interview_prep_full': True,
            'interview_prep_limited': True,
            'document_refinement': True,
            'story_bank': True,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': True,
            'negotiation_guidance': True,
            'negotiation_full': False,
            'conversation_memory': True,
            'dashboard_full': True,
            'dashboard_insights': True,
            'dashboard_benchmarking': False,
            'application_alerts': True,
            'career_level_assessment': False,
            'live_coaching': True,
        }
    },
    'coach': {
        'applications_per_month': -1,
        'resumes_per_month': -1,
        'cover_letters_per_month': -1,
        'henry_conversations_per_month': -1,
        'mock_interviews_per_month': -1,
        'coaching_sessions_per_month': 2,
        'coaching_session_minutes': 45,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': True,
            'application_tracker': True,
            'company_intelligence': True,
            'linkedin_recommendations': True,
            'linkedin_optimization': True,
            'interview_prep_full': True,
            'interview_prep_limited': True,
            'document_refinement': True,
            'story_bank': True,
            'pattern_analysis': True,
            'rejection_forensics': True,
            'salary_benchmarking': True,
            'negotiation_guidance': True,
            'negotiation_full': True,
            'conversation_memory': True,
            'dashboard_full': True,
            'dashboard_insights': True,
            'dashboard_benchmarking': True,
            'application_alerts': True,
            'career_level_assessment': True,
            'live_coaching': True,
        }
    },
}
```

---

## 2.3 Beta User Configuration

### Named Beta Users (Permanent Access)

```python
NAMED_BETA_USERS = {
    # Identify by email or user_id
    'jordan@example.com': {
        'tier': 'coach',
        'expires': None,  # Never expires
        'discount_after': 0,
    },
    'adam@example.com': {
        'tier': 'coach',
        'expires': None,
        'discount_after': 0,
    },
    'alex@example.com': {
        'tier': 'partner',
        'expires': None,
        'discount_after': 0,
    },
    'darnel@example.com': {
        'tier': 'coach',
        'expires': None,
        'discount_after': 0,
    },
    # Note: Quinn gets no special treatment - regular candidate
}
```

### Default Beta User Config (Other Beta Signups)

```python
# For any user who signed up before LAUNCH_DATE and is not in NAMED_BETA_USERS
DEFAULT_BETA_CONFIG = {
    'tier': 'partner',
    'expires_days_after_launch': 90,  # 3 months from launch
    'discount_after': 0,  # No discount after expiration
}

LAUNCH_DATE = datetime(2025, 1, 15)  # Update to actual launch date
```

### Migration Script

```python
def migrate_beta_users():
    """Run once before launch to set beta user flags"""
    
    # Get all users who signed up before launch
    beta_users = User.query.filter(User.created_at < LAUNCH_DATE).all()
    
    for user in beta_users:
        user.is_beta_user = True
        
        # Check if named beta user
        if user.email in NAMED_BETA_USERS:
            config = NAMED_BETA_USERS[user.email]
            user.beta_tier_override = config['tier']
            user.beta_expires_at = config['expires']
            user.beta_discount_percent = config['discount_after']
        else:
            # Default beta config
            user.beta_tier_override = DEFAULT_BETA_CONFIG['tier']
            user.beta_expires_at = LAUNCH_DATE + timedelta(days=DEFAULT_BETA_CONFIG['expires_days_after_launch'])
            user.beta_discount_percent = DEFAULT_BETA_CONFIG['discount_after']
        
        user.save()
```

---

## 2.4 Helper Functions

### Get Effective Tier

```python
def get_effective_tier(user) -> str:
    """
    Returns the user's effective tier, considering beta overrides.
    """
    # Check beta override first
    if user.is_beta_user and user.beta_tier_override:
        # Check if still valid
        if user.beta_expires_at is None or user.beta_expires_at > datetime.utcnow():
            return user.beta_tier_override
    
    # Fall back to subscription tier
    return user.tier or 'sourcer'
```

### Check Feature Access

```python
def check_feature_access(user, feature_name: str) -> dict:
    """
    Returns {
        'allowed': bool,
        'limited': bool,  # True if 'limited' access (not full)
        'upgrade_to': str or None,  # Tier needed to unlock
    }
    """
    tier = get_effective_tier(user)
    feature_value = TIER_LIMITS[tier]['features'].get(feature_name, False)
    
    if feature_value == True:
        return {'allowed': True, 'limited': False, 'upgrade_to': None}
    elif feature_value == 'limited':
        return {'allowed': True, 'limited': True, 'upgrade_to': get_unlock_tier(feature_name)}
    else:
        return {'allowed': False, 'limited': False, 'upgrade_to': get_unlock_tier(feature_name)}

def get_unlock_tier(feature_name: str) -> str:
    """Find the lowest tier that fully unlocks a feature"""
    tier_order = ['sourcer', 'recruiter', 'principal', 'partner', 'coach']
    for tier in tier_order:
        if TIER_LIMITS[tier]['features'].get(feature_name) == True:
            return tier
    return 'coach'
```

### Check Usage Limit

```python
def check_usage_limit(user, usage_type: str) -> dict:
    """
    Returns {
        'allowed': bool,
        'used': int,
        'limit': int,  # -1 means unlimited/strategic
        'remaining': int or None,
        'is_unlimited': bool,
    }
    """
    tier = get_effective_tier(user)
    limit_key = f'{usage_type}_per_month'
    limit = TIER_LIMITS[tier].get(limit_key, 0)
    
    # Get current period usage
    usage = get_or_create_current_period_usage(user.id)
    used = getattr(usage, f'{usage_type}_used', 0)
    
    if limit == -1:  # Unlimited/strategic
        return {
            'allowed': True,
            'used': used,
            'limit': -1,
            'remaining': None,
            'is_unlimited': True,
        }
    
    remaining = max(0, limit - used)
    return {
        'allowed': used < limit,
        'used': used,
        'limit': limit,
        'remaining': remaining,
        'is_unlimited': False,
    }
```

### Increment Usage

```python
def increment_usage(user, usage_type: str) -> None:
    """Increment usage counter for the current billing period"""
    usage = get_or_create_current_period_usage(user.id)
    field = f'{usage_type}_used'
    current = getattr(usage, field, 0)
    setattr(usage, field, current + 1)
    usage.updated_at = datetime.utcnow()
    usage.save()

def get_or_create_current_period_usage(user_id: str) -> UsageTracking:
    """Get or create usage tracking for current billing period"""
    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate period end (first of next month)
    if now.month == 12:
        period_end = period_start.replace(year=now.year + 1, month=1)
    else:
        period_end = period_start.replace(month=now.month + 1)
    
    usage = UsageTracking.query.filter_by(
        user_id=user_id,
        period_start=period_start
    ).first()
    
    if not usage:
        usage = UsageTracking(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
        )
        usage.save()
    
    return usage
```

### Get Upgrade Prompt

```python
def get_upgrade_prompt(current_tier: str, feature_name: str = None, usage_type: str = None) -> dict:
    """
    Returns upgrade messaging for paywalls.
    """
    tier_order = ['sourcer', 'recruiter', 'principal', 'partner', 'coach']
    tier_names = {
        'sourcer': 'Sourcer',
        'recruiter': 'Recruiter',
        'principal': 'Principal',
        'partner': 'Partner',
        'coach': 'Coach',
    }
    
    current_index = tier_order.index(current_tier)
    
    # Find next tier up
    if current_index < len(tier_order) - 1:
        next_tier = tier_order[current_index + 1]
        return {
            'upgrade_to': next_tier,
            'upgrade_name': tier_names[next_tier],
            'price': TIER_PRICES[next_tier],
            'message': f'Upgrade to {tier_names[next_tier]} to unlock this feature',
        }
    
    return None
```

---

## 2.5 API Endpoint Protection

### Decorator Pattern

```python
from functools import wraps

def require_feature(feature_name: str):
    """Decorator to protect endpoints by feature access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: User = Depends(get_current_user), **kwargs):
            access = check_feature_access(user, feature_name)
            if not access['allowed']:
                raise HTTPException(
                    status_code=403,
                    detail={
                        'error': 'feature_locked',
                        'feature': feature_name,
                        'upgrade_to': access['upgrade_to'],
                        'message': f'Upgrade to {access["upgrade_to"].title()} to access this feature'
                    }
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

def require_usage(usage_type: str):
    """Decorator to check and increment usage limits"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: User = Depends(get_current_user), **kwargs):
            usage = check_usage_limit(user, usage_type)
            if not usage['allowed']:
                raise HTTPException(
                    status_code=429,
                    detail={
                        'error': 'limit_reached',
                        'usage_type': usage_type,
                        'used': usage['used'],
                        'limit': usage['limit'],
                        'message': f'Monthly limit reached ({usage["used"]}/{usage["limit"]}). Upgrade for more.'
                    }
                )
            
            # Execute function
            result = await func(*args, user=user, **kwargs)
            
            # Increment usage after successful execution
            increment_usage(user, usage_type)
            
            return result
        return wrapper
    return decorator
```

### Example Protected Endpoints

```python
@app.post("/api/generate-resume")
@require_feature('job_fit_analysis')  # All tiers have this
@require_usage('resumes')  # But usage is limited
async def generate_resume(request: ResumeRequest, user: User = Depends(get_current_user)):
    # Generate tailored resume
    result = await resume_service.generate(request, user)
    return result


@app.post("/api/document-refinement")
@require_feature('document_refinement')  # Partner+ only
async def refine_document(request: RefinementRequest, user: User = Depends(get_current_user)):
    result = await document_service.refine(request, user)
    return result


@app.post("/api/mock-interview")
@require_feature('interview_prep_limited')  # Recruiter+ has some access
@require_usage('mock_interviews')
async def start_mock_interview(request: MockInterviewRequest, user: User = Depends(get_current_user)):
    # Check if recruiter tier - limit to recruiter screen format only
    tier = get_effective_tier(user)
    if tier == 'recruiter' and request.interview_type != 'recruiter_screen':
        raise HTTPException(
            status_code=403,
            detail={
                'error': 'feature_limited',
                'message': 'Recruiter tier only includes recruiter screen mock interviews. Upgrade to Principal for all interview types.'
            }
        )
    
    result = await mock_interview_service.start(request, user)
    return result


@app.get("/api/user/usage")
async def get_user_usage(user: User = Depends(get_current_user)):
    """Return current usage stats for the user"""
    tier = get_effective_tier(user)
    limits = TIER_LIMITS[tier]
    
    usage_types = [
        'applications',
        'resumes',
        'cover_letters', 
        'henry_conversations',
        'mock_interviews',
        'coaching_sessions'
    ]
    
    usage_stats = {}
    for usage_type in usage_types:
        usage_stats[usage_type] = check_usage_limit(user, usage_type)
    
    return {
        'tier': tier,
        'tier_display': tier.title(),
        'usage': usage_stats,
        'features': limits['features'],
    }
```

---

## 2.6 Frontend Integration

### API Response Handling

```javascript
// Handle feature locked response
async function callProtectedEndpoint(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        
        if (response.status === 403) {
            const error = await response.json();
            if (error.error === 'feature_locked') {
                showUpgradeModal({
                    feature: error.feature,
                    upgradeTo: error.upgrade_to,
                    message: error.message,
                });
                return null;
            }
        }
        
        if (response.status === 429) {
            const error = await response.json();
            if (error.error === 'limit_reached') {
                showLimitReachedModal({
                    usageType: error.usage_type,
                    used: error.used,
                    limit: error.limit,
                    message: error.message,
                });
                return null;
            }
        }
        
        return await response.json();
    } catch (err) {
        console.error('API error:', err);
        throw err;
    }
}
```

### Upgrade Modal Component

```javascript
function showUpgradeModal({ feature, upgradeTo, message }) {
    // Display modal with:
    // - Message explaining the locked feature
    // - Benefits of upgrading to the suggested tier
    // - Price of the upgrade tier
    // - CTA to upgrade
    // - Option to dismiss
}

function showLimitReachedModal({ usageType, used, limit, message }) {
    // Display modal with:
    // - Message showing current usage (e.g., "You've used 15/15 resumes this month")
    // - When the limit resets (first of next month)
    // - Option to upgrade for more
    // - CTA to upgrade
}
```

### Pre-check Before Showing Features

```javascript
// Fetch user's current tier and usage on app load
async function loadUserAccess() {
    const response = await fetch('/api/user/usage');
    const data = await response.json();
    
    // Store in app state
    window.userTier = data.tier;
    window.userFeatures = data.features;
    window.userUsage = data.usage;
}

// Check before rendering a feature
function canAccessFeature(featureName) {
    return window.userFeatures[featureName] === true || 
           window.userFeatures[featureName] === 'limited';
}

function isFeatureLimited(featureName) {
    return window.userFeatures[featureName] === 'limited';
}

function hasUsageRemaining(usageType) {
    const usage = window.userUsage[usageType];
    return usage.is_unlimited || usage.remaining > 0;
}
```

---

## 2.7 Database Migration Checklist

1. Add fields to User model:
   - `tier` (string, default 'sourcer')
   - `tier_started_at` (datetime, nullable)
   - `stripe_customer_id` (string, nullable)
   - `stripe_subscription_id` (string, nullable)
   - `is_beta_user` (boolean, default false)
   - `beta_tier_override` (string, nullable)
   - `beta_expires_at` (datetime, nullable)
   - `beta_discount_percent` (integer, default 0)

2. Create UsageTracking table

3. Run beta user migration script before launch

4. Create indexes:
   - `UsageTracking(user_id, period_start)` - for fast lookups
   - `User(stripe_customer_id)` - for webhook handling

---

## 2.8 Testing Checklist

### Tier Access Tests
- [ ] Sourcer cannot access screening_questions endpoint
- [ ] Recruiter can access screening_questions endpoint
- [ ] Recruiter gets 'limited' response for outreach_templates
- [ ] Principal gets full access to outreach_templates
- [ ] Partner can access document_refinement
- [ ] Coach can access pattern_analysis

### Usage Limit Tests
- [ ] Sourcer blocked after 3 applications
- [ ] Recruiter blocked after 15 applications
- [ ] Partner not blocked (unlimited)
- [ ] Usage resets at start of new month
- [ ] Usage increments after successful action

### Beta User Tests
- [ ] Jordan (coach, never expires) has coach access
- [ ] Alex (partner, never expires) has partner access
- [ ] Other beta user has partner access
- [ ] Other beta user loses access after 90 days
- [ ] Quinn has no special access (regular sourcer)

### Upgrade Flow Tests
- [ ] 403 response includes upgrade_to tier
- [ ] 429 response includes usage stats
- [ ] Frontend displays correct upgrade modal
- [ ] Upgrade CTA leads to pricing/checkout

---

# SUMMARY

## Phase 1 Deliverables
1. Pricing section with 5 tier cards
2. FAQ accordion with 8 questions
3. (Optional) How It Works 4-step section

## Phase 2 Deliverables
1. Database schema updates (User model + UsageTracking table)
2. Tier configuration constants
3. Beta user configuration and migration
4. Helper functions (get_effective_tier, check_feature_access, check_usage_limit, etc.)
5. API endpoint protection decorators
6. Frontend integration patterns
7. Tests for all access scenarios

## Launch Sequence
1. Implement Phase 1 (landing page) - can deploy immediately
2. Implement Phase 2 database changes - deploy before launch
3. Run beta user migration - run once before launch
4. Implement Phase 2 API protection - deploy at launch
5. Phase 3 (Stripe) - implement post-launch or in parallel
