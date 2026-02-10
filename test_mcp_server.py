import anyio
from mcp.server import Server
from mcp.server.stdio import stdio_server
# IMPORT THESE TYPES
from mcp.types import Tool, CallToolResult, TextContent

server = Server(name="test")

@server.list_tools()
async def list_tools():
    # Return a list of Tool objects, not dictionaries
    return [
        Tool(
            name="ping",
            description="health check",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "ping":
        # Return a CallToolResult object
        return CallToolResult(
            content=[TextContent(type="text", text="pong")]
        )
    raise ValueError("Unknown tool")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    anyio.run(main)



# import anyio
# from mcp.server import Server
# from mcp.server.stdio import stdio_server

# server = Server(name="test")

# @server.list_tools()
# async def list_tools():
#     return [
#         {
#             "name": "ping",
#             "description": "health check",
#             "inputSchema": {"type": "object"}
#         }
#     ]

# @server.call_tool()
# async def call_tool(name: str, arguments: dict):
#     if name == "ping":
#         return {"ok": True}
#     raise ValueError("Unknown tool")

# async def main():
#     # stdio_server() yields the communication streams
#     async with stdio_server() as (read_stream, write_stream):
#         # Pass the streams and initialization options to server.run()
#         await server.run(
#             read_stream,
#             write_stream,
#             server.create_initialization_options()
#         )

# if __name__ == "__main__":
#     anyio.run(main)
