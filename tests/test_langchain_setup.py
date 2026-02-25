"""
Smoke test: verify agent LLM works.
Run from project root: python tests/test_langchain_setup.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from app.config.agent_config import get_agent_llm

llm = get_agent_llm()
print("Using model:", llm.model_name)

response = llm.invoke("Who is the current PM of India? One line only.")
print("Response:", response.content)
