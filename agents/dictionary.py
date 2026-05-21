"""
Dictionary Agent — explains insurance jargon in plain language.
Has a quick-lookup cache for common terms to save API calls.
"""

from core.llm import invoke


DICTIONARY_PROMPT = """You are PolicySense's Dictionary mode. Explain insurance terms in simple, relatable language.

Rules:
- Use analogies and real-life examples
- If policy context is available, explain the term relative to THEIR policy
- Always explain the IMPACT on the user
- Warn about common misconceptions

User's policy context: {policy_context}
User's question: {question}

Format:
## 📖 The Term
**Simple explanation:** (1-2 sentences, no jargon)
**Real-life example:** (a scenario)
**Impact on you:** (how this affects their wallet/coverage)
**⚠️ Watch out:** (common trap, if any)"""

COMMON_TERMS = {
    "co-pay": "The percentage YOU pay out of pocket for each claim. If co-pay is 20% and your bill is ₹1 lakh, you pay ₹20,000.",
    "sub-limit": "A cap on specific expenses within your total coverage. Even if you have ₹10L cover, room rent might be capped at ₹5000/day.",
    "waiting period": "Time you must wait after buying the policy before you can claim for certain things.",
    "pre-existing disease": "Any condition you already had before buying the policy. Usually has a 2-4 year waiting period.",
    "sum insured": "The maximum amount your insurer will pay across all claims in a year.",
    "deductible": "The amount you pay first before insurance kicks in. Like a minimum threshold.",
    "no-claim bonus": "Discount on next year's premium if you don't make any claims this year.",
    "cashless": "Hospital bills paid directly by insurer to hospital. You don't pay upfront.",
    "reimbursement": "You pay the hospital first, then claim the money back from insurer.",
    "exclusion": "Things your policy will NEVER cover, no matter what.",
    "endorsement": "A change/addition to your existing policy mid-term.",
    "rider": "An add-on to your base policy for extra coverage (at extra cost).",
    "claim ratio": "Percentage of claims an insurer actually pays vs rejects. Higher = better for you.",
}


class DictionaryAgent:

    def explain(self, question: str, policy_context: str = "") -> str:
        q_lower = question.lower().strip("?. ")

        for term, definition in COMMON_TERMS.items():
            if term in q_lower and not policy_context:
                return (
                    f"## 📖 {term.title()}\n\n"
                    f"**Quick answer:** {definition}\n\n"
                    "Want me to explain how this applies to your specific policy? "
                    "Upload your policy document and ask again!"
                )

        return invoke(DICTIONARY_PROMPT.format(
            policy_context=policy_context or "No policy uploaded yet.",
            question=question,
        ))
