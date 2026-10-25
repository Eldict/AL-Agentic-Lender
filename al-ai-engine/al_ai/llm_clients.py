# Wrappers for Ollama, Groq and Gemini.
# A missing key, stopped server or failed call skips the provider instead of crashing.

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Callable

# provider name -> call function (filled in at the bottom)
PROVIDERS: dict[str, Callable[..., str]] = {}
# provider name -> check function, returns None if usable or a reason if not
AVAILABILITY: dict[str, Callable[[str], str | None]] = {}


@dataclass
class LLMReply:
    provider: str
    model: str
    text: str | None = None
    error: str | None = None

    @property
    def label(self) -> str:
        return f"{self.provider}/{self.model}"


# knows which providers can be used this run
@dataclass
class LLMRouter:
    timeout: int = 60
    active: list[tuple[str, str]] = field(default_factory=list)      # (provider, model)
    skipped: dict[str, str] = field(default_factory=dict)            # provider -> reason

    # checks every provider in config.yaml
    @classmethod
    def from_config(cls, cfg: dict, disabled: bool = False) -> "LLMRouter":
        router = cls(timeout=cfg["llm"].get("timeout_seconds", 60))
        for p in cfg["llm"]["providers"]:
            name, model = p["name"], p["model"]
            if disabled:
                router.skipped[name] = "LLMs turned off (--no-llm)"
            elif not p.get("enabled", True):
                router.skipped[name] = "disabled in config.yaml"
            elif name not in PROVIDERS:
                router.skipped[name] = "provider not implemented"
            else:
                reason = AVAILABILITY[name](model)
                if reason:
                    router.skipped[name] = reason
                else:
                    router.active.append((name, model))
        return router

    @property
    def numbers_only(self) -> bool:
        return not self.active

    # asks one provider; errors are caught and returned, never raised
    def ask(self, provider: str, model: str, system: str, prompt: str, want_json: bool = False) -> LLMReply:
        reply = LLMReply(provider, model)
        try:
            reply.text = PROVIDERS[provider](model=model, system=system, prompt=prompt,
                                             timeout=self.timeout, want_json=want_json).strip()
        except Exception as exc:
            reply.error = f"{type(exc).__name__}: {str(exc)[:200]}"
        return reply

    # asks providers in order, returns the first answer (used for summaries)
    def ask_first(self, system: str, prompt: str) -> LLMReply | None:
        last = None
        for provider, model in self.active:
            last = self.ask(provider, model, system, prompt)
            if last.text:
                return last
        return last

    # asks for JSON, validates it, retries once, then gives up
    def ask_json(self, provider: str, model: str, system: str, prompt: str,
                 validate: Callable[[dict], dict]) -> tuple[dict | None, LLMReply]:
        reply = self.ask(provider, model, system, prompt, want_json=True)
        for attempt in range(2):
            if reply.error:
                return None, reply
            try:
                return validate(extract_json(reply.text)), reply
            except (ValueError, KeyError, TypeError) as exc:
                if attempt == 1:
                    reply.error = f"invalid JSON after retry: {exc}"
                    return None, reply
                retry_prompt = (f"{prompt}\n\nYour previous answer was not valid ({exc}). "
                                "Reply with ONLY the JSON object, nothing else.")
                reply = self.ask(provider, model, system, retry_prompt, want_json=True)
        return None, reply


# --- Ollama (local) ---

def _ollama_host() -> str:
    return os.getenv("OLLAMA_HOST", "http://localhost:11434")


# checks Ollama is running and the model is pulled
def _ollama_available(model: str) -> str | None:
    try:
        import ollama
        names = [m.model for m in ollama.Client(host=_ollama_host(), timeout=3).list().models]
    except ImportError:
        return "ollama package not installed"
    except Exception:
        return f"Ollama not running at {_ollama_host()}"
    if not any(n == model or n.split(":")[0] == model for n in names):
        return f"model '{model}' not pulled (run: ollama pull {model})"
    return None


def _ollama_call(model, system, prompt, timeout, want_json):
    import ollama
    client = ollama.Client(host=_ollama_host(), timeout=timeout)
    resp = client.chat(model=model, messages=[{"role": "system", "content": system},
                                              {"role": "user", "content": prompt}],
                       format="json" if want_json else None, options={"temperature": 0.2})
    return resp.message.content


# --- Groq (cloud) ---

def _groq_available(model: str) -> str | None:
    if not os.getenv("GROQ_API_KEY"):
        return "GROQ_API_KEY not set"
    try:
        import groq  # noqa: F401
    except ImportError:
        return "groq package not installed"
    return None


def _groq_call(model, system, prompt, timeout, want_json):
    from groq import Groq
    client = Groq(timeout=timeout, max_retries=1)  # reads GROQ_API_KEY itself
    resp = client.chat.completions.create(
        model=model, temperature=0.2,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"} if want_json else None)
    return resp.choices[0].message.content


# --- Google Gemini (cloud) ---

def _gemini_available(model: str) -> str | None:
    if not os.getenv("GEMINI_API_KEY"):
        return "GEMINI_API_KEY not set"
    try:
        from google import genai  # noqa: F401
    except ImportError:
        return "google-genai package not installed"
    return None


def _gemini_call(model, system, prompt, timeout, want_json):
    from google import genai
    from google.genai import types
    client = genai.Client(http_options=types.HttpOptions(timeout=timeout * 1000))  # reads GEMINI_API_KEY itself; timeout in ms
    resp = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.2,
                                           response_mime_type="application/json" if want_json else None))
    return resp.text


PROVIDERS.update({"ollama": _ollama_call, "groq": _groq_call, "gemini": _gemini_call})
AVAILABILITY.update({"ollama": _ollama_available, "groq": _groq_available, "gemini": _gemini_available})


# pulls the JSON object out of a reply, even with ```json fences or extra text
def extract_json(text: str | None) -> dict:
    if not text:
        raise ValueError("empty reply")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("JSON is not an object")
    return data
