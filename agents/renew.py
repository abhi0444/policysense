"""
Renew Agent — helps users decide whether to renew, upgrade, or switch.
"""

import json
from core.llm import invoke, parse_json
from core.models import PolicySummary, UserProfile, RenewalAdvice


RENEWAL_PROMPT = """You are PolicySense, an unbiased renewal advisor. Analyze if the user should renew as-is, upgrade, or switch.

Current Policy:
{policy_json}

User's Situation:
- Age: {age}
- City: {city}
- Family members: {family}
- Income range: {income}
- Existing conditions: {conditions}
- Priorities: {priorities}

Life changes mentioned: {life_changes}

Return JSON:
{{
  "life_changes_detected": ["what changed that affects insurance needs"],
  "coverage_gaps": ["what they NEED but don't have"],
  "over_coverage": ["what they're paying for but don't need"],
  "recommendation": "Renew as-is / Upgrade / Consider switching — with reasoning",
  "action_items": ["specific steps before renewal"]
}}

Be honest. If the policy is fine, say so. Consider:
- Age bracket changes (premiums jump at 35, 45, 55)
- City tier (metro hospital costs vs non-metro)
- Family additions
- Inflation (is sum insured still adequate?)"""


class RenewAgent:

    def analyze_renewal(self, policy_summary: PolicySummary, profile: UserProfile,
                        life_changes: str = "") -> RenewalAdvice:
        raw = invoke(RENEWAL_PROMPT.format(
            policy_json=policy_summary.model_dump_json(),
            age=profile.age or "Not specified",
            city=profile.city or "Not specified",
            family=profile.family_members or "Not specified",
            income=profile.income_range or "Not specified",
            conditions=", ".join(profile.existing_conditions) or "None",
            priorities=", ".join(profile.priorities) or "Not specified",
            life_changes=life_changes or "None mentioned",
        ), json_mode=True)
        data = parse_json(raw)
        return RenewalAdvice(**data)
