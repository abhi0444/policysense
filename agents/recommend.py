"""
Recommend Agent — tells users what to LOOK FOR, never what to BUY.
We never name brands. Instead we give criteria like "look for X coverage".
"""

from core.llm import invoke
from core.models import UserProfile


RECOMMEND_PROMPT = """You are PolicySense, an unbiased insurance advisor. Recommend what KIND of policy the user should look for — NOT a specific brand.

User Profile:
- Age: {age}
- City: {city}
- Family members: {family}
- Income range: {income}
- Existing conditions: {conditions}
- Existing coverage: {existing}
- Priorities: {priorities}

Additional context: {context}

Provide:
## 🎯 What You Need
## 💰 Ideal Coverage Amount (based on city, income, family)
## ✅ Must-Have Features
## 🚫 What to Avoid
## 📋 Checklist Before Buying
## 💡 Pro Tips

RULES:
- NEVER recommend a specific brand or product
- Explain WHY a feature matters for THEIR situation
- Be honest about trade-offs"""


class RecommendAgent:

    def recommend(self, profile: UserProfile, context: str = "") -> str:
        return invoke(RECOMMEND_PROMPT.format(
            age=profile.age or "Not specified",
            city=profile.city or "Not specified",
            family=profile.family_members or "Not specified",
            income=profile.income_range or "Not specified",
            conditions=", ".join(profile.existing_conditions) or "None",
            existing=", ".join(profile.existing_coverage) or "None",
            priorities=", ".join(profile.priorities) or "Not specified",
            context=context or "None",
        ))
