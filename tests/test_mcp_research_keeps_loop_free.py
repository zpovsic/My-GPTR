"""MCP research used to call the sync ``MCPRetriever.search()`` from inside the server's event loop. That blocked
the loop while a second loop in a thread reused langchain-openai's shared HTTP connections, deadlocking the whole
server (even ``GET /`` stopped answering). The conductor must await ``search_async`` on its own loop instead."""
import asyncio
import unittest
from types import SimpleNamespace

from gpt_researcher.skills.researcher import ResearchConductor


class FakeMCPRetriever:
    def __init__(self, query, headers=None, query_domains=None, websocket=None, researcher=None):
        self.query = query

    def search(self, max_results=10):
        raise AssertionError("sync search() blocks the event loop and must not be used here")

    async def search_async(self, max_results=10):
        loop_ticked = asyncio.Event()
        asyncio.get_running_loop().call_soon(loop_ticked.set)
        await asyncio.wait_for(loop_ticked.wait(), timeout=2)
        return [{"title": "NVIDIA", "href": "https://example.com/nvda", "body": "earnings"}]


class MCPResearchLoopTests(unittest.IsolatedAsyncioTestCase):
    async def test_mcp_research_is_awaited_on_the_running_loop(self):
        researcher = SimpleNamespace(
            cfg=SimpleNamespace(max_search_results_per_query=5),
            verbose=False,
            websocket=None,
            headers={},
            query_domains=[],
        )
        conductor = ResearchConductor(researcher)

        results = await conductor._execute_mcp_research(FakeMCPRetriever, "Stock analysis on nvidia")

        self.assertEqual(results[0]["href"], "https://example.com/nvda")


if __name__ == "__main__":
    unittest.main()
