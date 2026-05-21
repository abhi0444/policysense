"""
PolicySense CLI demo — quick way to test without spinning up Streamlit.

Usage:
    python demo.py
    Then: /load path/to/policy.pdf
    Or just ask questions directly.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import route_intent
from agents.understand import UnderstandAgent
from agents.compare import CompareAgent
from agents.renew import RenewAgent
from agents.dictionary import DictionaryAgent
from agents.recommend import RecommendAgent
from core.models import UserProfile, PolicySummary

# init everything
understand = UnderstandAgent()
compare = CompareAgent()
renew = RenewAgent()
dictionary = DictionaryAgent()
recommend = RecommendAgent()

user_profile = UserProfile()
policy_summaries = {}


def load_pdf(path):
    """Load and parse a policy PDF."""
    from core.pdf_parser import extract_text_from_pdf

    text = extract_text_from_pdf(path)
    policy_id = os.path.basename(path)
    summary = understand.load_policy(text, policy_id)
    policy_summaries[policy_id] = summary

    print(f"\n✅ Loaded: {summary.get('product_name', policy_id)}")
    print(f"   Insurer: {summary.get('insurer', 'Unknown')}")
    print(f"   Type: {summary.get('policy_type', 'Unknown')}")
    print(f"   Sum Insured: {summary.get('sum_insured', 'Unknown')}")
    return policy_id


def load_text(text, name="pasted_policy"):
    """Load policy from pasted text."""
    summary = understand.load_policy(text, name)
    policy_summaries[name] = summary
    print(f"\n✅ Loaded: {summary.get('product_name', name)}")
    return name


def handle_message(msg, context=""):
    """Route to the right agent and get a response."""
    track = route_intent(msg, context)
    policy_id = next(iter(understand.policies), None)

    if track == "understand":
        if not policy_id:
            return "📄 No policy loaded. Use /load <path> or /paste to add one."
        return understand.ask(policy_id, msg)

    elif track == "compare":
        ids = list(policy_summaries.keys())
        if len(ids) < 2:
            return "⚖️ Need 2 policies to compare. Load another with /load <path>"
        s_a = PolicySummary(**policy_summaries[ids[0]])
        s_b = PolicySummary(**policy_summaries[ids[1]])
        return compare.compare_readable(s_a, s_b, msg)

    elif track == "renew":
        if not policy_id or not policy_summaries:
            return "🔄 Load your current policy first with /load <path>"
        s = PolicySummary(**next(iter(policy_summaries.values())))
        advice = renew.analyze_renewal(s, user_profile, msg)
        parts = [f"**Recommendation:** {advice.recommendation}"]
        if advice.coverage_gaps:
            parts.append(f"**Gaps:** {', '.join(advice.coverage_gaps)}")
        if advice.action_items:
            parts.append(f"**Actions:** {', '.join(advice.action_items)}")
        return "\n\n".join(parts)

    elif track == "dictionary":
        policy_text = understand.policies.get(policy_id, "")[:3000] if policy_id else ""
        return dictionary.explain(msg, policy_text)

    elif track == "recommend":
        return recommend.recommend(user_profile, msg)

    # fallback
    return dictionary.explain(msg)


def main():
    print("""
🛡️  PolicySense — Your Unbiased AI Insurance Advisor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"An AI that works for you, not the insurer."

Commands:
  /load <path>    Load a policy PDF
  /paste          Paste policy text manually
  /simplify       Get plain-language explanation of loaded policy
  /profile        Set your profile (age, city, etc.)
  /quit           Exit

Or just ask anything about insurance!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    history = []

    while True:
        try:
            msg = input("\n🧑 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye! 👋")
            break

        if not msg:
            continue

        if msg == "/quit":
            print("Bye! 👋")
            break

        elif msg.startswith("/load "):
            path = msg[6:].strip()
            if os.path.exists(path):
                load_pdf(path)
            else:
                print(f"❌ File not found: {path}")

        elif msg == "/paste":
            print("Paste your policy text (type END on a new line when done):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            load_text("\n".join(lines))

        elif msg == "/simplify":
            pid = next(iter(understand.policies), None)
            if pid:
                print("\n🤖 PolicySense:\n")
                print(understand.simplify_policy(pid))
            else:
                print("No policy loaded yet.")

        elif msg == "/profile":
            print("Tell me about yourself:")
            user_profile.age = int(input("  Age: ") or "0") or None
            user_profile.city = input("  City: ") or None
            user_profile.family_members = int(input("  Family members to cover: ") or "0") or None
            user_profile.income_range = input("  Income range (e.g. 8-12 LPA): ") or None
            conds = input("  Health conditions (comma-separated, or none): ")
            user_profile.existing_conditions = [c.strip() for c in conds.split(",") if c.strip()] if conds else []
            prios = input("  Priorities (e.g. low premium, no co-pay): ")
            user_profile.priorities = [p.strip() for p in prios.split(",") if p.strip()] if prios else []
            print("✅ Profile saved!")

        else:
            ctx = "\n".join(history[-4:])
            response = handle_message(msg, ctx)
            print(f"\n🤖 PolicySense:\n\n{response}")
            history.append(f"user: {msg}")
            history.append(f"assistant: {response[:200]}")


if __name__ == "__main__":
    main()
