"""
Orchestrator — figures out what the user wants and sends them to the right agent.
"""

from core.llm import invoke_fast

ROUTING_PROMPT = """Classify this user message into one of these tracks:
- "understand" — wants to understand their policy, ask questions about coverage
- "compare" — wants to compare two or more policies
- "renew" — asking about renewal, whether to continue/switch
- "dictionary" — asking what a term means
- "recommend" — wants advice on what policy to buy

User message: {message}
Context: {context}

Respond with ONLY one word: understand, compare, renew, dictionary, or recommend"""


def route_intent(message: str, context: str = "") -> str:
    result = invoke_fast(ROUTING_PROMPT.format(message=message, context=context))
    intent = result.strip().lower().strip('".')
    valid = {"understand", "compare", "renew", "dictionary", "recommend"}
    return intent if intent in valid else "understand"
