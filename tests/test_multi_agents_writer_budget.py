"""Reasoning models spend ``max_tokens`` on hidden reasoning before answering, so the multi-agent writer must get
``SMART_TOKEN_LIMIT`` instead of the 4000-token default (it returned empty answers until every retry failed), and
an LLM failure must surface as a clear error rather than ``'NoneType' object is not a mapping``."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from multi_agents.agents.utils.llms import call_model
from multi_agents.agents.writer import WriterAgent


@pytest.mark.asyncio
async def test_call_model_uses_the_smart_token_limit():
    cfg = SimpleNamespace(smart_token_limit=32000, smart_llm_provider="openai", llm_kwargs={})
    mock_ccc = AsyncMock(return_value="ok")
    with patch.dict(call_model.__globals__, {"create_chat_completion": mock_ccc, "Config": lambda: cfg}):
        await call_model([{"role": "user", "content": "hi"}], "gpt-6.1-sol")
    assert mock_ccc.call_args.kwargs["max_tokens"] == 32000


@pytest.mark.asyncio
async def test_writer_raises_a_clear_error_when_the_llm_gives_nothing():
    writer = WriterAgent()
    research_state = {"title": "NVIDIA", "research_data": [], "task": {"model": "gpt-6.1-sol"}}
    with patch("multi_agents.agents.writer.call_model", new=AsyncMock(return_value=None)):
        with pytest.raises(RuntimeError, match="Writer got no usable"):
            await writer.run(research_state)
