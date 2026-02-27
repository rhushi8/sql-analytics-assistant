#Responsibility:
#Talk to Ollama
#Handle temperature
#Centralize model logic

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:13b"


def query_llm(prompt, temperature=0):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"].strip()