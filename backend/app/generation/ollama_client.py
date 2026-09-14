import ollama

from app.config import settings

_client = ollama.Client(host=settings.ollama_host)


def generate(prompt: str) -> str:
    try:
        response = _client.chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Could not reach Ollama at {settings.ollama_host} with model {settings.ollama_model!r}. "
            f"Is Ollama running and is the model pulled? Try: ollama serve (and ollama pull {settings.ollama_model})"
        ) from exc
    return response["message"]["content"].strip()
