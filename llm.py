#Responsibility:
#Talk to Ollama
#Handle temperature
#Centralize model logic

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:13b"


class LLMError(RuntimeError):
    """Raised when the local LLM is unreachable or returns an unexpected response."""


def query_llm(prompt, temperature=0):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise LLMError(
            f"Could not reach Ollama at {OLLAMA_URL}. Is `ollama serve` running "
            f"and `{MODEL_NAME}` pulled?"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    try:
        return response.json()["response"].strip()
    except (ValueError, KeyError) as exc:
        raise LLMError(f"Unexpected LLM response format: {response.text[:200]}") from exc