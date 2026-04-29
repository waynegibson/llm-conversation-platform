from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from typing import Any

import httpx
from core.config import get_settings

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self, max_retries: int = 2) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_url.rstrip("/")
        self.timeout = settings.request_timeout_seconds
        self.max_retries = max_retries

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                    response = client.request(method, path, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt <= self.max_retries:
                    sleep_seconds = 0.2 * attempt
                    logger.warning("Ollama request failed, retrying", extra={"attempt": attempt})
                    time.sleep(sleep_seconds)
                    continue
                raise

        if last_error is not None:
            raise last_error
        raise RuntimeError("Unreachable retry state")

    def list_models(self) -> list[dict[str, Any]]:
        payload = self._request("GET", "/api/tags")
        return payload.get("models", [])

    def is_available(self) -> bool:
        try:
            self.list_models()
        except Exception:
            return False
        return True

    def chat(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        if stream:
            raise NotImplementedError(
                "Streaming support will be added in the next implementation step."
            )

        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if top_p is not None:
            options["top_p"] = top_p

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        started = time.perf_counter()
        data = self._request("POST", "/api/chat", json=payload)

        latency_ms = int((time.perf_counter() - started) * 1000)
        message = data.get("message", {})

        return {
            "content": message.get("content", ""),
            "prompt_tokens": data.get("prompt_eval_count"),
            "completion_tokens": data.get("eval_count"),
            "total_tokens": (data.get("prompt_eval_count") or 0) + (data.get("eval_count") or 0),
            "latency_ms": latency_ms,
            "request_payload": payload,
            "response_payload": data,
        }

    def chat_stream(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if top_p is not None:
            options["top_p"] = top_p

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": True,
        }
        if options:
            payload["options"] = options

        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            with client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    yield chunk
