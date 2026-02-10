import asyncio
from sentence_transformers import SentenceTransformer

from mcp_client import QdrantMCPClient
from llm import GroqLLM
from prompt import build_prompt

# Same embedding model as ingestion (CRITICAL)
EMBED_MODEL_NAME = "intfloat/e5-small-v2"

class TerminalRAGAgent:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBED_MODEL_NAME)
        self.mcp_client = QdrantMCPClient()
        self.llm = GroqLLM()

    def embed_query(self, text: str):
        return self.embedder.encode(text).tolist()

    async def ask(self, question: str, top_k: int = 5):
        print("\n[1] Embedding query...")
        query_vector = self.embed_query(question)

        print("[2] Calling MCP server (Qdrant search)...")
        results = await self.mcp_client.search(query_vector, top_k=top_k)

        if not results:
            return "Answer not found in the provided database."

        contexts = [item["payload"]["text"] for item in results]

        print("[3] Building RAG prompt...")
        prompt = build_prompt(contexts, question)

        print("[4] Querying Groq LLM...")
        answer = self.llm.generate(prompt)

        return answer


async def main():
    agent = TerminalRAGAgent()

    print("====================================")
    print("  MCP-based Legal RAG Terminal Agent ")
    print("====================================")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask your question: ").strip()
        if question.lower() in {"exit", "quit"}:
            break

        try:
            answer = await agent.ask(question, top_k=5)
            print("\n--- Answer ---")
            print(answer)
            print("--------------\n")
        except Exception as e:
            print("\n[ERROR]", str(e), "\n")


if __name__ == "__main__":
    asyncio.run(main())
