import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class QdrantMCPClient:
    def __init__(self):
        self.params = StdioServerParameters(
            command="python",
            args=["qdrant_mcp_server.py"]
        )

    async def search(self, query_vector, top_k=5):
        async with stdio_client(self.params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "qdrant_search",
                    {
                        "query_vector": query_vector,
                        "top_k": top_k
                    }
                )

                # return result.content[0].text
                return json.loads(result.content[0].text)
               

if __name__ == "__main__":
    async def test():
        client = QdrantMCPClient()
        dummy = [0.0] * 384
        print(await client.search(dummy, 2))

    asyncio.run(test())





# import asyncio
# from mcp.client.session import ClientSession
# from mcp.client.stdio import stdio_client, StdioServerParameters

# class QdrantMCPClient:
#     def __init__(self):
#         self.server_params = StdioServerParameters(
#             command="python",
#             args=["qdrant_mcp_server.py"]
#         )

#     async def _ensure_tool(self, session, tool_name: str):
#         tools = await session.list_tools()
#         names = [t["name"] for t in tools]
#         if tool_name not in names:
#             raise RuntimeError(f"MCP tool '{tool_name}' not found. Available: {names}")

#     async def search(self, query_vector, top_k=5):
#         async with stdio_client(self.server_params) as (read, write):
#             async with ClientSession(read, write) as session:
#                 await self._ensure_tool(session, "qdrant_search")

#                 result = await session.call_tool(
#                     name="qdrant_search",
#                     arguments={
#                         "query_vector": query_vector,
#                         "top_k": top_k
#                     }
#                 )

#                 return result["results"]

# if __name__ == "__main__":
#     async def test():
#         client = QdrantMCPClient()
#         dummy_vector = [0.0] * 384
#         res = await client.search(dummy_vector, top_k=2)
#         print("MCP OK:", res)

#     asyncio.run(test())
