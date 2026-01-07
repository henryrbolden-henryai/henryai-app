-- ============================================================================
-- ROLE INTERACTIONS ANALYTICS QUERIES
-- Admin queries for analyzing candidate behavior with role guidance
-- Version: 1.0
-- Date: January 2026
-- ============================================================================

-- ============================================================================
-- QUERY 1: Are candidates following guidance?
-- Shows how often candidates apply vs pass based on our recommendation
-- ============================================================================
SELECT
    recommendation,
    interaction_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY recommendation), 1) as pct_of_recommendation
FROM candidate_role_interactions
WHERE interaction_type IN ('applied', 'skipped', 'override')
  AND recommendation IS NOT NULL
GROUP BY recommendation, interaction_type
ORDER BY recommendation, interaction_type;

-- ============================================================================
-- QUERY 2: Override behavior analysis
-- How often do candidates ignore "Do Not Apply" guidance?
-- ============================================================================
SELECT
    DATE_TRUNC('week', interaction_at) as week,
    COUNT(*) FILTER (WHERE override_type = 'applied_despite_dna') as applied_despite_dna,
    COUNT(*) FILTER (WHERE override_type = 'applied_low_fit') as applied_low_fit,
    COUNT(*) FILTER (WHERE interaction_type = 'skipped' AND recommendation = 'Do Not Apply') as followed_dna_guidance,
    ROUND(
        COUNT(*) FILTER (WHERE override_type = 'applied_despite_dna') * 100.0 /
        NULLIF(COUNT(*) FILTER (WHERE recommendation = 'Do Not Apply'), 0), 1
    ) as dna_override_rate_pct
FROM candidate_role_interactions
WHERE recommendation = 'Do Not Apply'
GROUP BY DATE_TRUNC('week', interaction_at)
ORDER BY week DESC
LIMIT 12;

-- ============================================================================
-- QUERY 3: Fit score distribution for applied roles
-- Are candidates applying to appropriate-fit roles?
-- ============================================================================
SELECT
    CASE
        WHEN fit_score >= 80 THEN 'Excellent (80-100)'
        WHEN fit_score >= 60 THEN 'Good (60-79)'
        WHEN fit_score >= 40 THEN 'Moderate (40-59)'
        ELSE 'Low (0-39)'
    END as fit_bracket,
    COUNT(*) FILTER (WHERE interaction_type = 'applied') as applied_count,
    COUNT(*) FILTER (WHERE interaction_type = 'skipped') as skipped_count,
    COUNT(*) FILTER (WHERE interaction_type = 'override') as override_count,
    ROUND(AVG(fit_score) FILTER (WHERE interaction_type = 'applied'), 1) as avg_applied_fit
FROM candidate_role_interactions
WHERE fit_score IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- ============================================================================
-- QUERY 4: Reconsideration patterns
-- How often do candidates reconsider skipped roles?
-- ============================================================================
SELECT
    DATE_TRUNC('week', interaction_at) as week,
    COUNT(*) FILTER (WHERE interaction_type = 'skipped') as total_skipped,
    COUNT(*) FILTER (WHERE interaction_type = 'reconsidered') as reconsidered,
    ROUND(
        COUNT(*) FILTER (WHERE interaction_type = 'reconsidered') * 100.0 /
        NULLIF(COUNT(*) FILTER (WHERE interaction_type = 'skipped'), 0), 1
    ) as reconsider_rate_pct
FROM candidate_role_interactions
GROUP BY DATE_TRUNC('week', interaction_at)
ORDER BY week DESC
LIMIT 12;

-- ============================================================================
-- QUERY 5: Pass reasons breakdown
-- Why are candidates passing on roles?
-- ============================================================================
SELECT
    COALESCE(pass_reason, 'not_specified') as reason,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
FROM candidate_role_interactions
WHERE interaction_type = 'skipped'
GROUP BY pass_reason
ORDER BY count DESC;

-- ============================================================================
-- QUERY 6: Outcome tracking for override decisions
-- What happens when candidates ignore guidance?
-- ============================================================================
SELECT
    override_type,
    outcome,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY override_type), 1) as pct
FROM candidate_role_interactions
WHERE interaction_type = 'override'
  AND outcome IS NOT NULL
GROUP BY override_type, outcome
ORDER BY override_type, count DESC;

-- ============================================================================
-- QUERY 7: Daily activity summary
-- Overview of candidate-role interactions
-- ============================================================================
SELECT
    DATE(interaction_at) as date,
    COUNT(*) FILTER (WHERE interaction_type = 'analyzed') as analyzed,
    COUNT(*) FILTER (WHERE interaction_type = 'applied') as applied,
    COUNT(*) FILTER (WHERE interaction_type = 'skipped') as skipped,
    COUNT(*) FILTER (WHERE interaction_type = 'override') as overrides,
    COUNT(*) FILTER (WHERE interaction_type = 'reconsidered') as reconsidered,
    COUNT(DISTINCT user_id) as unique_users
FROM candidate_role_interactions
WHERE interaction_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(interaction_at)
ORDER BY date DESC;

-- ============================================================================
-- QUERY 8: Top companies candidates are passing on
-- Which companies are being skipped most often?
-- ============================================================================
SELECT
    company,
    COUNT(*) as skip_count,
    ROUND(AVG(fit_score), 1) as avg_fit_score,
    MODE() WITHIN GROUP (ORDER BY pass_reason) as most_common_reason
FROM candidate_role_interactions
WHERE interaction_type = 'skipped'
GROUP BY company
HAVING COUNT(*) >= 3
ORDER BY skip_count DESC
LIMIT 20;

-- ============================================================================
-- QUERY 9: User-level behavior summary
-- Per-user guidance adherence (for identifying patterns)
-- ============================================================================
SELECT
    user_id,
    COUNT(*) as total_interactions,
    COUNT(*) FILTER (WHERE interaction_type = 'applied') as applied,
    COUNT(*) FILTER (WHERE interaction_type = 'skipped') as skipped,
    COUNT(*) FILTER (WHERE interaction_type = 'override') as overrides,
    ROUND(
        COUNT(*) FILTER (WHERE interaction_type = 'override') * 100.0 /
        NULLIF(COUNT(*) FILTER (WHERE interaction_type IN ('applied', 'skipped', 'override')), 0), 1
    ) as override_rate_pct,
    ROUND(AVG(fit_score) FILTER (WHERE interaction_type = 'applied'), 1) as avg_applied_fit
FROM candidate_role_interactions
GROUP BY user_id
HAVING COUNT(*) >= 5
ORDER BY override_rate_pct DESC
LIMIT 50;

-- ============================================================================
-- QUERY 10: Guidance effectiveness by recommendation type
-- How well are our recommendations being followed?
-- ============================================================================
SELECT
    recommendation,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE
        (recommendation = 'Apply' AND interaction_type = 'applied') OR
        (recommendation = 'Do Not Apply' AND interaction_type = 'skipped') OR
        (recommendation = 'Apply with Caution' AND interaction_type IN ('applied', 'skipped'))
    ) as followed_guidance,
    COUNT(*) FILTER (WHERE
        (recommendation = 'Apply' AND interaction_type = 'skipped') OR
        (recommendation = 'Do Not Apply' AND interaction_type IN ('applied', 'override'))
    ) as deviated,
    ROUND(
        COUNT(*) FILTER (WHERE
            (recommendation = 'Apply' AND interaction_type = 'applied') OR
            (recommendation = 'Do Not Apply' AND interaction_type = 'skipped')
        ) * 100.0 / NULLIF(COUNT(*), 0), 1
    ) as follow_rate_pct
FROM candidate_role_interactions
WHERE recommendation IS NOT NULL
  AND interaction_type IN ('applied', 'skipped', 'override')
GROUP BY recommendation
ORDER BY total DESC;

-- ============================================================================
-- QUERY 11: Role journey analysis
-- Track complete journey for specific roles
-- ============================================================================
-- Example: Find roles that were skipped then reconsidered
SELECT
    c1.user_id,
    c1.company,
    c1.role_title,
    c1.interaction_at as first_skipped,
    c2.interaction_at as reconsidered_at,
    c3.interaction_at as final_action_at,
    c3.interaction_type as final_action,
    EXTRACT(DAY FROM c2.interaction_at - c1.interaction_at) as days_to_reconsider
FROM candidate_role_interactions c1
JOIN candidate_role_interactions c2
    ON c1.user_id = c2.user_id
    AND c1.company = c2.company
    AND c1.role_title = c2.role_title
    AND c2.interaction_type = 'reconsidered'
    AND c2.interaction_at > c1.interaction_at
LEFT JOIN candidate_role_interactions c3
    ON c2.user_id = c3.user_id
    AND c2.company = c3.company
    AND c2.role_title = c3.role_title
    AND c3.interaction_type IN ('applied', 'skipped')
    AND c3.interaction_at > c2.interaction_at
WHERE c1.interaction_type = 'skipped'
ORDER BY c1.interaction_at DESC
LIMIT 50;
