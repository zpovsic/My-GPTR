"""GPT-5.x point releases and GPT-6+ accept ``reasoning_effort="xhigh"`` and reject any temperature but the
default, so ``REASONING_EFFORT=xhigh`` must parse and both settings must reach those models correctly, including
new variants that are not listed by name."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gpt_researcher.config.config import Config
from gpt_researcher.llm_provider.generic.base import supports_reasoning_effort, supports_temperature
from gpt_researcher.utils.llm import create_chat_completion

GPT_REASONING_MODELS = ["gpt-5.6-terra", "gpt-5.6-sol", "gpt-6-astra", "gpt-6-luna", "gpt-6.1-sol"]


def test_xhigh_is_a_valid_reasoning_effort():
    assert Config.parse_reasoning_effort("xhigh") == "xhigh"


def test_unsupported_reasoning_effort_still_raises():
    with pytest.raises(ValueError, match="xhigh, high, medium, low"):
        Config.parse_reasoning_effort("max")


@pytest.mark.parametrize("model", GPT_REASONING_MODELS)
def test_gpt_reasoning_family_is_recognised(model):
    assert supports_reasoning_effort(model)
    assert not supports_temperature(model)


@pytest.mark.parametrize("model", ["gpt-4o", "gpt-4.1-mini", "gpt-5-chat-latest", "claude-3-5-sonnet"])
def test_other_models_keep_their_temperature(model):
    assert supports_temperature(model)
    assert not supports_reasoning_effort(model)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", GPT_REASONING_MODELS)
async def test_reasoning_models_get_reasoning_effort_and_no_temperature(monkeypatch, model):
    monkeypatch.delenv("LLM_KWARGS", raising=False)
    provider = MagicMock()
    provider.get_chat_response = AsyncMock(return_value="ok")
    with patch("gpt_researcher.utils.llm.get_llm", return_value=provider) as mock_get_llm:
        await create_chat_completion(
            messages=[{"role": "user", "content": "Generate a report"}],
            model=model,
            llm_provider="openai",
            temperature=0.4,
            reasoning_effort="xhigh",
        )
    kwargs = mock_get_llm.call_args.kwargs
    assert kwargs["reasoning_effort"] == "xhigh"
    assert kwargs["temperature"] is None
