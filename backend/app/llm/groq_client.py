# openRouterClient — thin wrapper around the OpenRouter SDK with structured output
import logging
import time
from functools import lru_cache
from typing import Any, Optional, Type
from openai import OpenAI
from pydantic import BaseModel

from app.config import getSettings, getYamlConfig

logger = logging.getLogger(__name__)


import hashlib

# Simple in-memory LLM cache
_llm_cache = {}

def _get_llm_cache_key(kwargs: dict) -> str:
    # Safely hash the parameters to identify identical LLM calls
    key_str = str(kwargs)
    return hashlib.md5(key_str.encode()).hexdigest()

class GroqClient:
    """Single-responsibility wrapper: one LLM call, one place to add retry/logging.
    (Kept name as GroqClient to avoid breaking imports across the app)
    """

    def __init__(self) -> None:
        settings = getSettings()
        # Initialize OpenAI client pointing to OpenRouter
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self._model = "openai/gpt-oss-120b:free"

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.5,
        maxTokens: int = 4096,
        tools: Optional[list[dict]] = None,
        toolChoice: Optional[str] = None,
    ) -> Any:
        kwargs: dict = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": maxTokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = toolChoice or "auto"

        # 2. LLM-Level Caching
        cache_key = _get_llm_cache_key(kwargs)
        if cache_key in _llm_cache:
            logger.debug(f"LLM Cache hit for model={self._model}")
            return _llm_cache[cache_key]

        response = self._client.chat.completions.create(**kwargs)
        
        # Safely log token usage if available
        tokens_in = response.usage.prompt_tokens if response.usage else 0
        tokens_out = response.usage.completion_tokens if response.usage else 0
        logger.debug(f"OpenRouter call model={self._model}: tokens_in={tokens_in} tokens_out={tokens_out}")
        
        _llm_cache[cache_key] = response
        return response

    def structuredChat(
        self,
        messages: list[dict],
        responseModel: Type[BaseModel],
        temperature: float = 0.2,
        maxTokens: int = 2048,
    ) -> BaseModel:
        """Force JSON output matching responseModel schema via a system-level instruction."""
        schemaJson = responseModel.model_json_schema()
        systemAddition = (
            f"\n\nRespond ONLY with valid JSON that strictly matches this schema:\n{schemaJson}\n"
            "No markdown, no explanation, just the JSON object."
        )
        enrichedMessages = list(messages)
        if enrichedMessages and enrichedMessages[0]["role"] == "system":
            enrichedMessages[0] = {
                "role": "system",
                "content": enrichedMessages[0]["content"] + systemAddition,
            }
        else:
            enrichedMessages.insert(0, {"role": "system", "content": systemAddition})

        response = self.chat(enrichedMessages, temperature=temperature, maxTokens=maxTokens)
        rawContent = response.choices[0].message.content or "{}"

        import json
        rawContent = rawContent.strip()
        if rawContent.startswith("```"):
            rawContent = rawContent.split("```")[1]
            if rawContent.startswith("json"):
                rawContent = rawContent[4:]
        
        try:
            parsed = json.loads(rawContent)
            return responseModel.model_validate(parsed)
        except Exception as e:
            logger.error(f"Failed to parse JSON from response: {rawContent}")
            raise

    def plainChat(
        self,
        messages: list[dict],
        temperature: float = 0.5,
        maxTokens: int = 4096,
    ) -> str:
        response = self.chat(messages, temperature=temperature, maxTokens=maxTokens)
        return response.choices[0].message.content or ""


@lru_cache()
def getGroqClient() -> GroqClient:
    return GroqClient()
