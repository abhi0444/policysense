"""
Understand Agent — handles policy extraction and user Q&A.

Not using vector store here because most policies fit within context window.
If we hit policies > 30 pages we'll need to switch to RAG.
"""

import json
from core.llm import invoke, parse_json


EXTRACTION_PROMPT = """You are an insurance policy analyst. Extract structured information from this policy document.
If something is not clearly stated, mark it as "Not specified".

Policy Text:
{policy_text}

Return a JSON object with these exact fields:
{{
  "insurer": "company name",
  "product_name": "policy/product name",
  "policy_type": "Health/Life/Motor/Travel",
  "sum_insured": "total coverage amount",
  "premium": "annual premium",
  "policy_term": "duration",
  "coverages": [{{"name": "...", "limit": "...", "sub_limit": "...", "copay": "...", "waiting_period": "..."}}],
  "exclusions": [{{"description": "...", "category": "General/Pre-existing/Specific"}}],
  "waiting_periods": ["..."],
  "key_benefits": ["..."],
  "key_limitations": ["..."]
}}"""

QA_PROMPT = """You are PolicySense, an unbiased AI insurance advisor. Answer the user's question about their policy.

Rules:
- Answer ONLY based on the policy text below
- If the answer isn't in the policy, say "I couldn't find this in your policy document"
- Use simple, plain language
- Proactively warn about relevant exclusions or limitations

Policy text:
{policy_text}

User's question: {question}"""

SIMPLIFY_PROMPT = """You are PolicySense. Explain this insurance policy in plain, simple language.
Use these sections:

## What You're Covered For (The Good Stuff)
## What You're NOT Covered For (Watch Out!)
## Important Waiting Periods
## Hidden Gotchas (sub-limits, co-pays, caps)
## Bottom Line (1 paragraph: is this good? biggest risk?)

Policy text:
{policy_text}"""


class UnderstandAgent:
    def __init__(self):
        self.policies = {}

    def load_policy(self, policy_text: str, policy_id: str) -> dict:
        self.policies[policy_id] = policy_text
        raw = invoke(EXTRACTION_PROMPT.format(policy_text=policy_text[:10000]), json_mode=True)
        return parse_json(raw)

    def simplify_policy(self, policy_id: str) -> str:
        text = self.policies.get(policy_id, "")
        if not text:
            return "No policy loaded yet."
        return invoke(SIMPLIFY_PROMPT.format(policy_text=text[:10000]))

    def ask(self, policy_id: str, question: str) -> str:
        text = self.policies.get(policy_id)
        if not text:
            return "Please upload a policy first."
        return invoke(QA_PROMPT.format(policy_text=text[:10000], question=question))
