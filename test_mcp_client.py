import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main():
    params = StdioServerParameters(
        command="python",
        args=["test_mcp_server.py"]
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # MANDATORY: Perform the initialization handshake first
            await session.initialize()
            
            # Now you can proceed with other requests
            tools = await session.list_tools()
            print("TOOLS:", tools)

            result = await session.call_tool("ping", {})
            print("PING RESULT:", result)


asyncio.run(main())
