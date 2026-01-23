#!/usr/bin/env python3
"""LLM module Setup"""
import os
import asyncio
from openai import AsyncOpenAI

from dotenv import load_dotenv

load_dotenv()


# Get the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

# Single shared async client instances
llm_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
)

LLM_SEMAPHORE = asyncio.Semaphore(30)

async def call_llm( **kwargs):
    async with LLM_SEMAPHORE:
        response = await llm_client.chat.completions.create(**kwargs,
        )
        return response

async def stream_llm(**kwargs):
    # optional: reuse same semaphore or a separate one
    async with LLM_SEMAPHORE:
        return await llm_client.chat.completions.create(stream=True, **kwargs)



