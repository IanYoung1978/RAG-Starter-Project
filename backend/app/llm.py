"""Talking to the chat model.

Everything that knows about Ollama lives here, so swapping to another model
or provider later means changing this one file.
"""

import httpx

from app import config


def chat(messages: list[dict], temperature: float = 0.2) -> str:
    """Send a conversation to the model and return its reply.

    messages is a list like:
        [{"role": "system", "content": "standing instructions"},
         {"role": "user", "content": "the question"}]

    Low temperature makes answers more consistent and less inventive,
    which suits factual questions about your data.
    """
    response = httpx.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={
            "model": config.CHAT_MODEL,
            "messages": messages,
            "stream": False,  # wait for the whole answer instead of word by word
            "options": {"temperature": temperature},
        },
        timeout=120,  # the first call loads the model onto the GPU, which takes a while
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
