import os, json, re
import httpx
from dotenv import load_dotenv
from app.schemas import TestCase

load_dotenv()

PROMPT_TEMPLATE = """You are a QA engineer reviewing requirements for a Class II medical device.
Given the requirement text below, output ONLY a JSON array of 3 to 5 test cases.
Each item must have exactly these keys: "title", "steps" (array of strings), "expected_result".
Do not include markdown code fences, explanations, or any text outside the JSON array.

Requirement text:
{text}
"""


class LLMGenerationError(Exception):
    pass


def _call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```(json)?', '', text)
    text = re.sub(r'```$', '', text)
    return text.strip()


def generate_test_cases(text: str, max_retries: int = 1):
    prompt = PROMPT_TEMPLATE.format(text=text)
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            raw = _call_groq(prompt)
            cleaned = _strip_fences(raw)
            data = json.loads(cleaned)
            if not isinstance(data, list):
                raise ValueError("Expected a JSON array")
            validated = [TestCase(**item) for item in data]
            if 3 <= len(validated) <= 5:
                return validated
            raise ValueError(f"Expected 3-5 test cases, got {len(validated)}")
        except Exception as e:
            last_error = e
            continue

    raise LLMGenerationError(f"LLM output failed validation after {max_retries + 1} attempts: {last_error}")