#!/usr/bin/env python3
"""LLM module Setup"""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Get the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

# Initialize the LLM client
llm_client = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
    model="gpt-4.1-mini",
    temperature=0.2,
    max_tokens=1536
)


# Initialize the LLM client for suggestions
suggestion_llm_client = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
    model="gpt-4.1-mini",
    temperature=0.5,
    max_tokens=124
)

# Streaming LLM client
llm_client_main = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
    model="gpt-4.1-mini",
    temperature=0.3,
    max_tokens=4096,
    streaming=False,
)

# Formatting 
formatter_llm_client = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=4096,
    streaming=False,

)
