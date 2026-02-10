import anyio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult
from qdrant import QdrantStore

server = Server(name="qdrant-mcp")

store = QdrantStore(ensure_collection=False)

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="qdrant_search",
            description="Search vectors in Qdrant",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_vector": {
                        "type": "array",
                        "items": {"type": "number"}
                    },
                    "top_k": {
                        "type": "integer",
                        "default": 5
                    }
                },
                "required": ["query_vector"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "qdrant_search":
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text="Unknown tool")]
        )

    results = store.search(
        query_vector=arguments["query_vector"],
        top_k=arguments.get("top_k", 5)
    )

    # Send as JSON string (SDK-compatible)
    return CallToolResult(
#         content=[TextContent(type="text", text=str(results))]
        content=[TextContent(type="text", text=json.dumps(results))]
    )


async def main():
    async with stdio_server() as (read, write):
        await server.run(
            read,
            write,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    anyio.run(main)



