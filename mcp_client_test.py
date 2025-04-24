from mcp import ClientSession
from mcp.client.sse import sse_client
import asyncio
from mcpclient import MCPClient

async def connect_to_sse(server_url: str = "http://localhost:5000/sse") -> None:
    # 1) open the SSE transport
    async with sse_client(url=server_url) as (recv, send):
        # 2) open the MCP session
        async with ClientSession(recv, send) as client:
            # 3) initialize the session
            await client.initialize()

            # 4) list tools
            list_resp = await client.list_tools()
            print("Available tools:")
            for t in list_resp.tools:
                print(f" • {t.name}: {t.description}")

            # 5) call your `add` tool
            print(f"client in test script for tool call: {client}")
            call_resp = await client.call_tool("add", {"a": 2, "b": 5})
            print("add(2,5) =", call_resp.content)

            # call_duckduckgo = await client.call_tool("search",{"query":"give me an online mcp server, so far i have only seen mcp server which needs docker or install locally using npx"})
            # print("search('what is mcp?') =", call_duckduckgo)
            # fetch_duckduckgo= await client.call_tool("fetch_content",{"url":"https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html"})
            # print("details from url =", fetch_duckduckgo)

if __name__ == "__main__":
    asyncio.run(connect_to_sse())

# mcpclient = MCPClient(name="Duckduckgosearch", server_url="http://localhost:5000/sse")

# mc
