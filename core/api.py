"""
FastAPI backend for PolicySense.
Same functionality as CLI/Streamlit but as REST endpoints.
"""

import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agents.orchestrator import route_intent
from agents.understand import UnderstandAgent
from agents.compare import CompareAgent
from agents.renew import RenewAgent
from agents.dictionary import DictionaryAgent
from agents.recommend import RecommendAgent
from core.pdf_parser import extract_text_from_pdf, is_valid_pdf
from core.models import UserProfile, PolicySummary

app = FastAPI(title="PolicySense API", version="1.0.0")

understand_agent = UnderstandAgent()
compare_agent = CompareAgent()
renew_agent = RenewAgent()
dictionary_agent = DictionaryAgent()
recommend_agent = RecommendAgent()

policies: dict[str, dict] = {}


class ChatRequest(BaseModel):
    message: str
    policy_id: str | None = None
    context: str = ""


class RecommendRequest(BaseModel):
    profile: UserProfile
    context: str = ""


@app.post("/upload")
async def upload_policy(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    if not is_valid_pdf(tmp_path):
        os.unlink(tmp_path)
        raise HTTPException(400, "Could not extract text from PDF.")

    text = extract_text_from_pdf(tmp_path)
    os.unlink(tmp_path)

    policy_id = file.filename
    summary = understand_agent.load_policy(text, policy_id)
    policies[policy_id] = {"text": text, "summary": summary}
    return {"policy_id": policy_id, "summary": summary}


@app.post("/chat")
async def chat(req: ChatRequest):
    track = route_intent(req.message, req.context)

    if track == "understand":
        if not req.policy_id or req.policy_id not in policies:
            return {"track": track, "response": "Please upload a policy first."}
        response = understand_agent.ask(req.policy_id, req.message)

    elif track == "compare":
        ids = list(policies.keys())
        if len(ids) < 2:
            return {"track": track, "response": "Need at least 2 policies to compare."}
        s_a = PolicySummary(**policies[ids[0]]["summary"])
        s_b = PolicySummary(**policies[ids[1]]["summary"])
        response = compare_agent.compare_readable(s_a, s_b, req.message)

    elif track == "renew":
        if not req.policy_id or req.policy_id not in policies:
            return {"track": track, "response": "Upload your current policy first."}
        summary = PolicySummary(**policies[req.policy_id]["summary"])
        advice = renew_agent.analyze_renewal(summary, UserProfile(), req.message)
        response = (
            f"**Recommendation:** {advice.recommendation}\n\n"
            f"**Gaps:** {', '.join(advice.coverage_gaps)}\n\n"
            f"**Actions:** {', '.join(advice.action_items)}"
        )

    elif track == "dictionary":
        ctx = ""
        if req.policy_id and req.policy_id in policies:
            ctx = policies[req.policy_id]["text"][:3000]
        response = dictionary_agent.explain(req.message, ctx)

    elif track == "recommend":
        response = recommend_agent.recommend(UserProfile(), req.message)

    else:
        response = dictionary_agent.explain(req.message)

    return {"track": track, "response": response}


@app.post("/recommend")
async def recommend(req: RecommendRequest):
    return {"response": recommend_agent.recommend(req.profile, req.context)}


@app.get("/policies")
async def list_policies():
    return {pid: p["summary"] for pid, p in policies.items()}


@app.get("/health")
async def health():
    return {"status": "ok"}
