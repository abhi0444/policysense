"""PolicySense — Streamlit Chat UI."""

import os
import sys
import tempfile
import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from agents.orchestrator import route_intent
from agents.understand import UnderstandAgent
from agents.compare import CompareAgent
from agents.renew import RenewAgent
from agents.dictionary import DictionaryAgent
from agents.recommend import RecommendAgent
from core.pdf_parser import extract_text_from_pdf, is_valid_pdf
from core.models import UserProfile, PolicySummary

# --- page setup ---
st.set_page_config(page_title="PolicySense", page_icon="🛡️", layout="wide")
st.title("🛡️ PolicySense")
st.caption("*An AI that works for you, not the insurer.*")

# --- session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "policies" not in st.session_state:
    st.session_state.policies = {}
if "user_profile" not in st.session_state:
    st.session_state.user_profile = UserProfile()
if "active_track" not in st.session_state:
    st.session_state.active_track = None


@st.cache_resource
def get_agents():
    return {
        "understand": UnderstandAgent(),
        "compare": CompareAgent(),
        "renew": RenewAgent(),
        "dictionary": DictionaryAgent(),
        "recommend": RecommendAgent(),
    }


agents = get_agents()

# --- sidebar: policy upload + track selection ---
with st.sidebar:
    st.header("📄 Your Policies")

    uploaded_files = st.file_uploader(
        "Upload policy PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload your insurance policy documents to get started",
    )

    if uploaded_files:
        for f in uploaded_files:
            fid = f.name
            if fid not in st.session_state.policies:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(f.read())
                    tmp_path = tmp.name

                if is_valid_pdf(tmp_path):
                    with st.spinner(f"Processing {fid}..."):
                        text = extract_text_from_pdf(tmp_path)
                        summary = agents["understand"].load_policy(text, fid)
                        st.session_state.policies[fid] = {"text": text, "summary": summary}
                    st.success(f"✅ {fid} loaded!")
                else:
                    st.error(f"❌ {fid} — can't extract text. Might be a scanned image.")
                os.unlink(tmp_path)

    # show loaded policies
    if st.session_state.policies:
        st.divider()
        for pid, pdata in st.session_state.policies.items():
            s = pdata["summary"]
            name = s.get("product_name", pid) if isinstance(s, dict) else getattr(s, "product_name", pid)
            insurer = s.get("insurer", "") if isinstance(s, dict) else getattr(s, "insurer", "")
            st.markdown(f"**{name}**")
            st.caption(f"{insurer}")

    st.divider()
    st.header("🎯 Tracks")
    tracks = {
        "understand": "📖 Understand — Explain my policy",
        "compare": "⚖️ Compare — Compare policies",
        "renew": "🔄 Renew — Should I renew?",
        "dictionary": "📚 Dictionary — What does X mean?",
        "recommend": "🎯 Recommend — What should I buy?",
    }
    for track_id, label in tracks.items():
        if st.button(label, key=f"track_{track_id}", use_container_width=True):
            st.session_state.active_track = track_id

# --- chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- welcome message on first load ---
if not st.session_state.messages:
    welcome = """👋 Hey! I'm **PolicySense** — your unbiased AI insurance advisor.

I don't sell insurance. I don't take commissions. I work for **you**.

Here's what I can help with:
- 📖 **Understand** — Upload a policy and I'll explain it in plain English
- ⚖️ **Compare** — Upload two policies and I'll show you the real differences
- 🔄 **Renew** — Tell me about your life changes and I'll advise on renewal
- 📚 **Dictionary** — Ask me what any insurance term means
- 🎯 **Recommend** — Tell me about yourself and I'll tell you what to look for

**Start by uploading a policy PDF** (sidebar) or just ask me anything!"""
    st.chat_message("assistant").markdown(welcome)
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# --- handle user input ---
if prompt := st.chat_input("Ask me anything about insurance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # figure out which agent to use
    context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
    track = st.session_state.active_track or route_intent(prompt, context)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            first_pid = next(iter(st.session_state.policies), None)
            policy_text = st.session_state.policies[first_pid]["text"] if first_pid else ""

            if track == "understand":
                if first_pid:
                    response = agents["understand"].ask(first_pid, prompt)
                else:
                    response = "Please upload a policy PDF first (use the sidebar), then ask me anything about it!"

            elif track == "compare":
                pids = list(st.session_state.policies.keys())
                if len(pids) >= 2:
                    s_a = st.session_state.policies[pids[0]]["summary"]
                    s_b = st.session_state.policies[pids[1]]["summary"]
                    # handle both dict and PolicySummary objects
                    if isinstance(s_a, dict):
                        s_a = PolicySummary(**s_a)
                    if isinstance(s_b, dict):
                        s_b = PolicySummary(**s_b)
                    response = agents["compare"].compare_readable(s_a, s_b, prompt)
                else:
                    response = "I need at least 2 policy PDFs to compare. Upload them in the sidebar!"

            elif track == "renew":
                if first_pid:
                    s = st.session_state.policies[first_pid]["summary"]
                    if isinstance(s, dict):
                        s = PolicySummary(**s)
                    advice = agents["renew"].analyze_renewal(s, st.session_state.user_profile, prompt)
                    response = f"## 🔄 Renewal Analysis\n\n**Recommendation:** {advice.recommendation}\n\n"
                    if advice.coverage_gaps:
                        response += "### ⚠️ Coverage Gaps\n" + "\n".join(f"- {g}" for g in advice.coverage_gaps) + "\n\n"
                    if advice.action_items:
                        response += "### ✅ Action Items\n" + "\n".join(f"- {a}" for a in advice.action_items)
                else:
                    response = "Upload your current policy first, then tell me about life changes and I'll advise!"

            elif track == "dictionary":
                ctx = policy_text[:3000] if policy_text else ""
                response = agents["dictionary"].explain(prompt, ctx)

            elif track == "recommend":
                response = agents["recommend"].recommend(st.session_state.user_profile, prompt)

            else:
                response = agents["dictionary"].explain(prompt)

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
