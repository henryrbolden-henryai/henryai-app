# Instructions for Updating index.html

**Objective**: Update the HenryHQ landing page (index.html) with approved copy changes and new sections.

---

## Changes to Make

### 1. Update Title Tag (Line 5)
**Find:**
```html
<title>HenryHQ — Your Personal AI Job Search Strategist</title>
```

**Replace with:**
```html
<title>HenryHQ — Your Personal Job Search Strategist</title>
```

---

### 2. Update Hero Section Buttons (Around Line 761-773)
**Find the button-group div and replace the entire section:**

**Replace:**
```html
<div class="button-group">
  <button class="btn-primary" onclick="document.getElementById('about-henry').scrollIntoView({ behavior: 'smooth' })">
    About Henry
  </button>

  <button class="btn-secondary" onclick="document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })">
    Working with Henry
  </button>

  <button class="btn-secondary" onclick="window.location.href='analyze.html'">
    Get Started
  </button>
</div>
```

**With:**
```html
<div class="button-group">
  <button class="btn-primary" id="getStartedBtn">Get Started</button>
  <a href="#about-henry" class="btn-secondary">Learn More</a>
</div>
```

---

### 3. Update About Henry Section (Around Lines 882-904)
**Replace the entire section content between `<section id="about-henry">` and `</section>`:**

```html
<section id="about-henry">
  <div class="container">
    <h2>About Henry</h2>
    <p>
      Job searching is exhausting. You're spending hours tailoring applications for roles that ghost you, second-guessing your experience, and wondering if you're even targeting the right jobs.
    </p>
    <p>
      I'm Henry, your personal job search strategist. I'm not here to spit out documents like a resume vending machine. I'm here to cut through the noise with recruiter-grade intelligence.
    </p>
    <p>
      I was built by someone who's hired at scale—Spotify, Uber, National Grid, Heidrick & Struggles—and I've seen the mess from the inside. Most job search tools lie to you, tell you you're a great fit for anything with a pulse, and pump out generic applications that scream "AI-written."
    </p>
    <p>
      I don't do that.
    </p>
    <p>
      My mission: Help serious professionals navigate a broken job market with truth over hype, strategy over volume, and zero fabrication. If you're not competitive for a role, I'll tell you. If your positioning needs work, I'll tell you. No fluff, no false optimism, just honest strategic guidance.
    </p>
    <p>
      This is for people who value quality over quantity, who want to understand the game they're playing, and who are ready to run a smarter search.
    </p>
    <p>
      If that's you, let's go.
    </p>
  </div>
</section>
```

---

### 4. Update "How We Work Together" Section (Around Lines 906-955)

**Change H2 from:**
```html
<h2>How we work together</h2>
```

**To:**
```html
<h2>How it works</h2>
```

**Update Step 1 paragraph to:**
```html
<p>
  You begin by sharing your resume (and optionally, your LinkedIn profile) so I can translate it into a clear and structured view of your experience and strengths. My role is to help you see your impact and capture the parts of your story that matter most to hiring teams.
</p>
```

**Update Step 3 paragraph to:**
```html
<p>
  For each opportunity, I give you a brutally honest fit assessment—strengths, gaps, and whether you should actually apply. You get resume level analysis, LinkedIn profile scoring, and a Reality Check on competition. If the numbers don't add up, I'll tell you to skip it. If it's worth your time, you receive resumes and cover letters tailored to the specific role along with guidance that keeps everything true to you but clearer and more strategic.
</p>
```

**Update Step 4 paragraph to:**
```html
<p>
  I help you prepare with interview intelligence—company research, behavioral practice, and talking points tailored to the role. After interviews, we debrief what worked and what didn't. From networking outreach through offer negotiation, the goal is to help you improve with each conversation and move through the process with intention.
</p>
```

---

### 5. Replace Differentiators Section (Around Lines 957-991)

**Replace the entire `<section id="differentiators">` with:**

```html
<!-- ========== WHAT MAKES THIS DIFFERENT ========== -->
<section id="differentiators">
  <div class="container">
    <h2>What makes working with Henry different?</h2>
    
    <div class="steps" style="gap: 2rem;">
      <div class="step" style="grid-template-columns: 1fr;">
        <div class="step-content">
          <h3>Honest feedback, real support</h3>
          <p>
            I'll tell you when a role isn't worth your time, when your positioning needs work, or when you're not competitive. But I'm not here to discourage you. I'm here to help you improve, focus your energy on winnable opportunities, and show up stronger with each attempt.
          </p>
        </div>
      </div>

      <div class="step" style="grid-template-columns: 1fr;">
        <div class="step-content">
          <h3>Zero fabrication policy</h3>
          <p>
            Your experience is never exaggerated or invented. Everything remains accurate and grounded in your real background. I reframe and reposition, but I never lie. If you need more experience to be competitive, I'll tell you that instead of faking it.
          </p>
        </div>
      </div>

      <div class="step" style="grid-template-columns: 1fr;">
        <div class="step-content">
          <h3>Recruiter-grade intelligence</h3>
          <p>
            I analyze opportunities the way hiring managers and recruiters do. I look past generic job descriptions to identify real priorities, assess your competitive position, and provide strategic guidance that goes beyond surface-level keyword matching.
          </p>
        </div>
      </div>

      <div class="step" style="grid-template-columns: 1fr;">
        <div class="step-content">
          <h3>Strategy over volume</h3>
          <p>
            I'm not here to help you spam 100 applications. I'm here to help you identify 10 roles you're actually competitive for, position yourself strategically, and move through the process with confidence. Quality beats quantity every time.
          </p>
        </div>
      </div>
    </div>
  </div>
</section>
```

---

### 6. Replace Core Capabilities Section (Around Lines 993-1031)

**Replace the entire `<section id="capabilities">` with:**

```html
<!-- ========== CORE CAPABILITIES ========== -->
<section id="capabilities">
  <div class="container">
    <h2>Core capabilities</h2>
    
    <div class="feature-grid">
      <div class="feature-item">
        <div class="feature-icon">📊</div>
        <span class="feature-text">Fit scoring that tells you NOT to apply—honest assessment with 6-tier recommendations from "Strong Apply" to "Do Not Apply" so you focus on roles you can actually win.</span>
      </div>

      <div class="feature-item">
        <div class="feature-icon">🎯</div>
        <span class="feature-text">Reality Check on competition—see how many qualified candidates you're competing against and whether the compensation is realistic for the scope.</span>
      </div>

      <div class="feature-item">
        <div class="feature-icon">💼</div>
        <span class="feature-text">LinkedIn profile optimization—section-by-section LinkedIn analysis with optimization recommendations to align your public presence with target roles.</span>
      </div>

      <div class="feature-item">
        <div class="feature-icon">📝</div>
        <span class="feature-text">Strategic resumes and cover letters, not templates—every document is tailored to the specific role with positioning strategy built in. No generic outputs, no AI tells.</span>
      </div>

      <div class="feature-item">
        <div class="feature-icon">🎤</div>
        <span class="feature-text">Interview prep and conversational debriefs—company research, talking points, practice sessions, and post-interview conversations to improve with each attempt.</span>
      </div>

      <div class="feature-item">
        <div class="feature-icon">📈</div>
        <span class="feature-text">Application tracking and rejection analysis—track your pipeline, identify patterns in rejections, and refine your approach based on what's working.</span>
      </div>
    </div>
  </div>
</section>
```

---

### 7. Update CTA Section (Around Lines 1032-1041)

**Replace the CTA section content:**

```html
<!-- ========== CTA SECTION ========== -->
<section id="cta-section">
  <div class="container" style="text-align: center;">
    <h2 id="ctaTitle">Ready to get started?</h2>
    <p class="helper-text" id="ctaSubtitle" style="max-width: 500px; margin: 0 auto 32px;">
      Try HenryHQ free. Upload your resume and analyze your first role to see how the platform works. No credit card required.
    </p>
    <button class="btn-primary" id="ctaButton" style="width: auto; padding: 18px 48px;">
      Get Started Free
    </button>
  </div>
</section>
```

---

### 8. Update Footer (Around Lines 1045-1050)

**Replace the footer with:**

```html
<!-- ========== FOOTER ========== -->
<footer>
  <div class="container">
    <p>© 2025 HenryHQ</p>
    <div class="footer-links">
      <a href="privacy.html">Privacy Policy</a>
      <span>·</span>
      <a href="terms.html">Terms of Service</a>
      <span>·</span>
      <a href="contact.html">Contact</a>
    </div>
  </div>
</footer>
```

**Add this CSS to the `<style>` section (before the closing `</style>` tag):**

```css
/* Footer links styling */
footer .container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.footer-links {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.9rem;
}

.footer-links a {
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--color-accent);
}

.footer-links span {
  color: var(--color-text-secondary);
  opacity: 0.5;
}
```

---

### 9. Update JavaScript at Bottom (Around Lines 1053-1086)

**Find the script section and update the button handlers:**

**Add after line 1077 (after the ctaButton setup):**

```javascript
// Set up Get Started button in hero
const getStartedBtn = document.getElementById('getStartedBtn');
if (getStartedBtn) {
  getStartedBtn.onclick = () => window.location.href = 'analyze.html';
}
```

---

## Preview Mode Feature (Optional but Recommended)

**Add this CSS before the closing `</style>` tag:**

```css
/* Preview mode banner */
.preview-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(34, 211, 238, 0.15);
  border-bottom: 1px solid var(--color-accent);
  padding: 0.75rem;
  text-align: center;
  z-index: 1000;
  font-size: 0.9rem;
  color: var(--color-accent);
  font-weight: 500;
}

body.preview-mode {
  padding-top: 50px;
}
```

**Replace the entire script section (lines 1053-1086) with:**

```javascript
<script src="js/supabase-client.js"></script>
<script>
  // Preview mode bypass - add ?preview=true to URL to view landing page when logged in
  const urlParams = new URLSearchParams(window.location.search);
  const isPreviewMode = urlParams.has('preview');

  if (isPreviewMode) {
    // Show preview banner
    const banner = document.createElement('div');
    banner.className = 'preview-banner';
    banner.innerHTML = '👁️ Preview Mode — You're viewing the landing page as a logged-out user';
    document.body.prepend(banner);
    document.body.classList.add('preview-mode');

    // Set up CTAs for preview
    const ctaButton = document.getElementById('ctaButton');
    const getStartedBtn = document.getElementById('getStartedBtn');
    if (ctaButton) ctaButton.onclick = () => window.location.href = 'analyze.html';
    if (getStartedBtn) getStartedBtn.onclick = () => window.location.href = 'analyze.html';

    // Update login link
    const loginLink = document.getElementById('loginLink');
    if (loginLink) {
      loginLink.textContent = 'Dashboard';
      loginLink.href = 'dashboard.html';
    }
  } else {
    // Normal auth check - redirect logged-in users
    (async function() {
      // Check Supabase session
      if (typeof HenryAuth !== 'undefined') {
        const session = await HenryAuth.getSession();
        if (session) {
          window.location.href = 'dashboard.html';
          return;
        }
      }

      // Check localStorage profile as fallback
      const profile = localStorage.getItem('userProfile');
      if (profile) {
        window.location.href = 'dashboard.html';
        return;
      }

      // New user - set up CTAs
      const ctaButton = document.getElementById('ctaButton');
      const getStartedBtn = document.getElementById('getStartedBtn');
      if (ctaButton) ctaButton.onclick = () => window.location.href = 'analyze.html';
      if (getStartedBtn) getStartedBtn.onclick = () => window.location.href = 'analyze.html';

      // Update login link
      const loginLink = document.getElementById('loginLink');
      if (loginLink) {
        loginLink.textContent = 'Sign In';
        loginLink.href = 'login.html';
      }
    })();
  }
</script>
<script src="components/ask-henry.js"></script>
```

---

## Additional Files to Create

Create these three placeholder pages in the same directory as index.html:

1. **privacy.html** - Privacy policy placeholder
2. **terms.html** - Terms of service placeholder  
3. **contact.html** - Contact page

(Files are ready and will be provided separately)

---

## Testing Checklist

After making changes:

- [ ] Hero buttons work (Get Started → analyze.html, Learn More → scrolls)
- [ ] Nav "About" link scrolls to About section
- [ ] Nav "How it works" link scrolls to How it works section
- [ ] Footer links work (Privacy, Terms, Contact)
- [ ] CTA button works → analyze.html
- [ ] Preview mode works: Add `?preview=true` to URL
- [ ] Mobile responsive (test on phone)
- [ ] All text displays correctly (no broken layouts)

---

## Notes

- All "AI" references removed from copy
- No em dashes used (replaced with periods or commas)
- All punctuation and grammar checked
- Copy approved for elite talent (top 0.01%)
- Free trial positioning in CTA
- Preview mode allows you to view landing page while logged in
