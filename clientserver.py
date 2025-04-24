from utils.logger import logger
from mcpclientmanager import ClientManager
from openai import OpenAI
from config import settings
import asyncio
from openai.types.chat import ChatCompletionToolParam



client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def main():
    logger.info("Starting ClientManager")
    clientmanager = ClientManager()
    clientmanager.load_servers("mcpcentralconfig.yaml")
    await clientmanager.connect_to_all_servers()
    mcp_tools = clientmanager.tools
    print(f"list of all tools connected: {mcp_tools}")
    all_tools = [
    ChatCompletionToolParam(
        type="function",
        function={
            "name": f'{tool["service_name"]}00_{tool["tool_name"]}',
            "description": tool["tool_description"],
            "parameters": tool["tool_parameters"],
        },
    )
    for tool in mcp_tools
]
    # result = await clientmanager.process_tool_call(clientmanager.tools)
    # print(result[0].content)
    print(f"all  tools after the chatcompletiontoolparam change: {all_tools}")
    query = input("Enter a query: ")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"User's query: {query}"}],
        tools=all_tools,
        tool_choice="auto",
        temperature=0.0,
    )
    print(f"response from LLM: {response}")
    print("Tool calls from LLM:", response.choices[0].message.tool_calls)

    results = await clientmanager.process_tool_call(
        response.choices[0].message.tool_calls
    )
    print(f"results from the tool calls: {results}")
    await clientmanager.cleanup()
    
## figure out a way to include service name, version into the process call so that we can easily identify the client session from self.dict without it if a 2 different servers have same servername, tool name it will break the system since we dont know the session_id

if __name__ == "__main__":
    asyncio.run(main())
