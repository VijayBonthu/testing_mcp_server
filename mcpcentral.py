from utils.logger import logger
from mcpclientmanager import ClientManager
from openai import OpenAI
from config import settings
import asyncio
from openai.types.chat import ChatCompletionToolParam
from mcp.server.fastmcp import FastMCP, Context
from starlette.applications import Starlette
from starlette.routing import Mount
from startlette import create_starlette_app
import uvicorn
from llm_sanitize.sanitize_response import response_sanitize


client = OpenAI(api_key=settings.OPENAI_API_KEY)

mcp = FastMCP('mcp server for user')

app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app())
    ]
)

@mcp.tool()
async def main(query:str):
    """Take care of all the question for real time data"""
    logger.info("Starting ClientManager")
    clientmanager = ClientManager()
    clientmanager.load_servers("mcpservers.yaml")
    await clientmanager.connect_to_all_servers()
    mcp_tools = clientmanager.tools
    logger.info(f"list of all tools connected: {mcp_tools}")
    all_tools = [
    ChatCompletionToolParam(
        type="function",
        function={
            "name": f'{tool["service_name"]}_{tool["tool_name"]}',
            "description": tool["tool_description"],
            "parameters": tool["tool_parameters"],
        },
    )
    for tool in mcp_tools
]
    # result = await clientmanager.process_tool_call(clientmanager.tools)
    # print(result[0].content)
    logger.info(f"all  tools after the chatcompletiontoolparam change: {all_tools}")
    # query = input("Enter a query: ")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"User's query: {query}"}],
        tools=all_tools,
        tool_choice="auto",
        temperature=0.0,
    )
    logger.info(f"response from LLM: {response}")
    logger.info("Tool calls from LLM:", response.choices[0].message.tool_calls)

    results = await clientmanager.process_tool_call(
        response.choices[0].message.tool_calls
    )
    logger.info(f"results from the tool calls: {results}")
    mcp_tool_response = [content.text for result in results for content in result.content if content.type == "text"]
    mcp_tool_response_dict = {f"result_{index}": text for index, text in enumerate(mcp_tool_response)}
    # for result in results:
    #     for content in result.content:
    #         if content.type == "text":
    #             logger.info(f"content text: {content.text}")
    logger.info(f"content text: {mcp_tool_response_dict}")
    send_response = await response_sanitize(user_query=query, response=mcp_tool_response_dict)
    logger.info(f"response from sanitize llm: {send_response}")
    await clientmanager.cleanup()
    return send_response
    
#TODO
#needs to return the result to clientsever.py so that it can process the data.

if __name__ == "__main__":
    # asyncio.run(main())
    starlette_app = create_starlette_app(
        mcp_server=mcp._mcp_server, api_key=None,debug=True
    )
    uvicorn.run(starlette_app, host='127.0.0.1',port=5200)
    