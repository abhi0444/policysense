"""
LLM client — supports multiple providers so we can switch easily.
Using Groq for the POC (free, fast). Bedrock for production.
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")


def parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw.strip())


def invoke(prompt: str, max_tokens: int = 4096, json_mode: bool = False) -> str:
    if LLM_PROVIDER == "groq":
        return _call_groq(prompt, max_tokens, json_mode)
    elif LLM_PROVIDER == "openai":
        return _call_openai(prompt, max_tokens, json_mode)
    elif LLM_PROVIDER == "ollama":
        return _call_ollama(prompt, max_tokens, json_mode)
    elif LLM_PROVIDER == "bedrock":
        return _call_bedrock(prompt, max_tokens, json_mode)
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def invoke_fast(prompt: str, max_tokens: int = 20) -> str:
    if LLM_PROVIDER == "groq":
        return _call_groq(prompt, max_tokens, False, model="llama-3.1-8b-instant")
    elif LLM_PROVIDER == "openai":
        return _call_openai(prompt, max_tokens, False, model="gpt-4o-mini")
    elif LLM_PROVIDER == "ollama":
        return _call_ollama(prompt, max_tokens, False)
    elif LLM_PROVIDER == "bedrock":
        return _call_bedrock(prompt, max_tokens, False, model="anthropic.claude-3-haiku-20240307-v1:0")
    return invoke(prompt, max_tokens)


def _call_groq(prompt, max_tokens, json_mode, model=None):
    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    msgs = [{"role": "user", "content": prompt}]
    if json_mode:
        msgs.insert(0, {"role": "system", "content": "Respond ONLY with valid JSON."})
    resp = client.chat.completions.create(model=model, messages=msgs, max_tokens=max_tokens)
    return resp.choices[0].message.content


def _call_openai(prompt, max_tokens, json_mode, model=None):
    from openai import OpenAI

    client = OpenAI()
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    msgs = [{"role": "user", "content": prompt}]
    if json_mode:
        msgs.insert(0, {"role": "system", "content": "Respond with valid JSON only."})
    resp = client.chat.completions.create(model=model, messages=msgs, max_tokens=max_tokens, **kwargs)
    return resp.choices[0].message.content


def _call_ollama(prompt, max_tokens, json_mode, model=None):
    import requests

    model = model or os.getenv("OLLAMA_MODEL", "llama3")
    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    if json_mode:
        prompt = "Respond ONLY with valid JSON.\n\n" + prompt
    resp = requests.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
    return resp.json()["response"]


def _call_bedrock(prompt, max_tokens, json_mode, model=None):
    import boto3

    region = os.getenv("AWS_REGION", "us-east-1")
    model = model or os.getenv("BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
    client = boto3.client("bedrock-runtime", region_name=region)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if json_mode:
        body["system"] = "Respond ONLY with valid JSON."

    resp = client.invoke_model(modelId=model, body=json.dumps(body), contentType="application/json")
    result = json.loads(resp["body"].read())
    return result["content"][0]["text"]
