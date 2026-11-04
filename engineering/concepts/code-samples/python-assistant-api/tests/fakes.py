"""Fake implementations of the Retriever/LLMClient interfaces for testing
without any real external service.

See: ../../../interview/interview-01/20-python-assistant-api-deep-dive.md
"""


class FakeRetriever:
    def __init__(self, results):
        self.results = results

    async def search(self, query, allowed_groups, k):
        return self.results


class FakeLLM:
    def __init__(self, response=None):
        self.response = response or {"answer": "default answer", "cited_ids": []}

    async def generate(self, question, chunks):
        return self.response
