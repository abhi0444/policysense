"""
Compare Agent — side-by-side policy comparison with gotcha detection.
"""

import json
from core.llm import invoke, parse_json
from core.models import PolicySummary, ComparisonResult


COMPARE_PROMPT = """You are PolicySense, an unbiased insurance policy comparison expert.
Compare these two policies and help the user understand the differences.

Policy A: {policy_a_name}
{policy_a_json}

Policy B: {policy_b_name}
{policy_b_json}

User's needs/priorities: {user_context}

Return JSON:
{{
  "better_in_policy_a": ["..."],
  "better_in_policy_b": ["..."],
  "same_in_both": ["..."],
  "hidden_gotchas": ["tricky differences that could catch someone off guard"],
  "verdict": "clear recommendation based on user needs"
}}

Be specific with numbers. Don't be vague."""

READABLE_PROMPT = """You are PolicySense. Based on this comparison data, write a clear, conversational explanation.

Comparison Data:
{comparison_json}

Policy A: {policy_a_name}
Policy B: {policy_b_name}

Format:
## 🏆 Where {policy_a_name} Wins
## 🏆 Where {policy_b_name} Wins
## ⚠️ Hidden Gotchas (Read This!)
## 💡 My Take

Keep it conversational. Use examples. Highlight what actually matters."""


class CompareAgent:

    def compare(self, summary_a: PolicySummary, summary_b: PolicySummary,
                user_context: str = "") -> ComparisonResult:
        raw = invoke(COMPARE_PROMPT.format(
            policy_a_name=summary_a.product_name,
            policy_a_json=summary_a.model_dump_json(),
            policy_b_name=summary_b.product_name,
            policy_b_json=summary_b.model_dump_json(),
            user_context=user_context or "Not specified",
        ), json_mode=True)
        data = parse_json(raw)
        return ComparisonResult(**data)

    def compare_readable(self, summary_a: PolicySummary, summary_b: PolicySummary,
                         user_context: str = "") -> str:
        result = self.compare(summary_a, summary_b, user_context)
        return invoke(READABLE_PROMPT.format(
            comparison_json=result.model_dump_json(),
            policy_a_name=summary_a.product_name,
            policy_b_name=summary_b.product_name,
        ))
