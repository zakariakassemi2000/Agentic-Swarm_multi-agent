import os
import asyncio
from openai import AsyncOpenAI
from groq import AsyncGroq
from core.config import (
    OPENROUTER_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY, HF_TOKEN,
    OPENROUTER_MODEL, GROQ_MODEL, DEEPSEEK_MODEL,
    DEFAULT_TEMPERATURE, MAX_TOKENS,
)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://synapse-studio.ai",
    "X-Title": "Agentic Swarm",
}

# ── HuggingFace – use models that actually work on serverless inference ──
HF_BASE_URL = "https://router.huggingface.co/hf-inference/v1"
HF_MODELS = [
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "HuggingFaceH4/zephyr-7b-beta",
]

# ── Groq fallback models (each has separate rate limits) ──
GROQ_FALLBACK_MODELS = [
    GROQ_MODEL,                     # llama-3.3-70b-versatile
    "llama-3.1-8b-instant",         # smaller, higher rate limit
    "gemma2-9b-it",                 # another option
]

MAX_RETRIES = 2
RETRY_DELAY = 3  # seconds between full retry cycles


class AsyncLLMProvider:
    """Async LLM provider with aggressive fallback chain and retry logic."""

    async def stream_complete(
        self,
        system: str,
        user_prompt: str,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
    ):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ]

        for attempt in range(MAX_RETRIES):
            # ── 1. OpenRouter ──
            if OPENROUTER_API_KEY:
                try:
                    client = AsyncOpenAI(
                        api_key=OPENROUTER_API_KEY,
                        base_url=OPENROUTER_BASE_URL,
                        default_headers=OPENROUTER_HEADERS,
                    )
                    resp = await client.chat.completions.create(
                        model=OPENROUTER_MODEL,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    )
                    token_count = 0
                    async for chunk in resp:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta.content or ""
                            if delta:
                                token_count += 1
                                yield delta
                    if token_count > 0:
                        return
                except Exception as e:
                    print(f"[OpenRouter] FAIL: {e}")

            # ── 2. Groq (try multiple models) ──
            if GROQ_API_KEY:
                for groq_model in GROQ_FALLBACK_MODELS:
                    try:
                        client = AsyncGroq(api_key=GROQ_API_KEY)
                        resp = await client.chat.completions.create(
                            model=groq_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=min(max_tokens, 1024),
                            stream=True,
                        )
                        token_count = 0
                        async for chunk in resp:
                            if chunk.choices and len(chunk.choices) > 0:
                                delta = chunk.choices[0].delta.content or ""
                                if delta:
                                    token_count += 1
                                    yield delta
                        if token_count > 0:
                            return
                    except Exception as e:
                        print(f"[Groq/{groq_model}] FAIL: {e}")

            # ── 3. DeepSeek ──
            if DEEPSEEK_API_KEY:
                try:
                    client = AsyncOpenAI(
                        api_key=DEEPSEEK_API_KEY,
                        base_url="https://api.deepseek.com/v1",
                    )
                    resp = await client.chat.completions.create(
                        model=DEEPSEEK_MODEL,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    )
                    token_count = 0
                    async for chunk in resp:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta.content or ""
                            if delta:
                                token_count += 1
                                yield delta
                    if token_count > 0:
                        return
                except Exception as e:
                    print(f"[DeepSeek] FAIL: {e}")

            # ── 4. HuggingFace (try multiple models) ──
            if HF_TOKEN:
                for hf_model in HF_MODELS:
                    try:
                        client = AsyncOpenAI(
                            api_key=HF_TOKEN,
                            base_url=HF_BASE_URL,
                        )
                        resp = await client.chat.completions.create(
                            model=hf_model,
                            messages=messages,
                            temperature=min(temperature, 0.9),
                            max_tokens=min(max_tokens, 800),
                            stream=True,
                        )
                        token_count = 0
                        async for chunk in resp:
                            if chunk.choices and len(chunk.choices) > 0:
                                delta = chunk.choices[0].delta.content or ""
                                if delta:
                                    token_count += 1
                                    yield delta
                        if token_count > 0:
                            return
                    except Exception as e:
                        print(f"[HuggingFace/{hf_model}] FAIL: {e}")

            # ── All failed this attempt — wait before retry ──
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_DELAY * (attempt + 1)
                print(f"[LLM] All providers failed. Retrying in {wait}s... (attempt {attempt+1}/{MAX_RETRIES})")
                await asyncio.sleep(wait)

        yield "[All LLM providers are rate-limited. Please wait a few minutes and try again.]"


def get_llm_provider():
    return AsyncLLMProvider()
