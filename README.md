# PolicySense — Your Unbiased AI Insurance Advisor

> *"An AI that works for you, not the insurer."*

## The Problem

- 65% of Indians don't understand their own insurance policies ([BW Marketing World, 2026](https://www.bwmarketingworld.com/article/65-indians-admit-they-dont-understand-insurance-policies-despite-owning-them-report-561360))
- IRDAI fined PolicyBazaar ₹5 crore for biased product promotions
- Platforms use dark patterns to push high-commission products
- No tool exists that is genuinely on the consumer's side

## What PolicySense Does

An AI-powered, multi-track insurance advisor that is **100% user-centric** with **zero brand bias**.

### Tracks

| Track | What it does |
|-------|-------------|
| **Understand** | Upload a policy PDF → get plain-language explanation, chat with your policy |
| **Compare** | Compare 2 policies side-by-side → see differences, hidden gotchas |
| **Renew** | Analyze if your current policy still fits your life → get renewal advice |
| **Dictionary** | Explain insurance jargon in context → "What does co-pay mean for ME?" |
| **Recommend** | Answer questions about your life → get unbiased criteria for what to buy |

## Architecture

```
User (Streamlit Chat UI)
        │
        ▼
Orchestrator Agent (intent routing)
        │
        ├── Understand Agent (RAG over uploaded policy)
        ├── Compare Agent (structured extraction + diff)
        ├── Renew Agent (life-change analysis + gap detection)
        ├── Dictionary Agent (context-aware jargon buster)
        └── Recommend Agent (needs assessment → criteria generation)
        │
        ▼
Core Services: PDF Parser │ LLM │ Vector Store │ Structured Extraction
```

## Tech Stack

- **Python 3.11+**
- **Amazon Bedrock** (Claude 3 Sonnet — LLM backbone)
- **LangChain** (agent orchestration)
- **ChromaDB** (vector store for policy RAG)
- **pdfplumber** (PDF text extraction)
- **Pydantic** (structured data models)
- **Streamlit** (demo UI)
- **FastAPI** (API layer)

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure AWS credentials (must have Bedrock access)
aws configure
# Or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

cp .env.example .env
# Edit .env if you want to change region or model
```

## Run

```bash
# API server
uvicorn core.api:app --reload

# UI (separate terminal)
streamlit run ui/app.py
```

## Project Structure

```
policysense/
├── agents/
│   ├── orchestrator.py    # Routes user intent to correct agent
│   ├── understand.py      # Policy understanding + Q&A
│   ├── compare.py         # Policy comparison
│   ├── renew.py           # Renewal advisor
│   ├── dictionary.py      # Jargon buster
│   └── recommend.py       # New policy recommendation
├── core/
│   ├── api.py             # FastAPI endpoints
│   ├── pdf_parser.py      # PDF extraction
│   ├── models.py          # Pydantic data models
│   └── vector_store.py    # ChromaDB operations
├── ui/
│   └── app.py             # Streamlit chat interface
├── data/                  # Sample policies for demo
├── requirements.txt
├── .env.example
└── README.md
```

## Design Decisions

1. **No brand recommendations** — recommends criteria (coverage amount, features to look for), never specific products
2. **RAG over user's own policy** — answers are grounded in their actual document
3. **Multi-agent architecture** — each track is a specialized agent, orchestrator routes based on intent
4. **Structured extraction** — policies are parsed into typed Pydantic models for reliable comparison
5. **Conversational** — not a form-fill, but a natural chat experience

## Failure Modes & Mitigations

| Failure | Mitigation |
|---------|-----------|
| Scanned/image PDF | Detect and inform user; suggest text-based PDF |
| LLM hallucination | Ground all answers in extracted text; cite page numbers |
| Ambiguous policy language | Flag uncertainty; show original text alongside interpretation |
| User uploads non-insurance doc | Classify document type first; reject gracefully |

---

Built for the [Build at Damco](https://www.damcogroup.com/build-at-damco) challenge.
