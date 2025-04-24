from mcpclient import MCPClient
from typing import List, Dict, Any
from p_model_type import tools_list_details
import yaml
from utils.logger import setup_logger
import asyncio
from openai.types.chat import ChatCompletionMessageToolCall
from openai import OpenAI
import json

logger = setup_logger()
class ClientManager:
    def __init__(self):
        self.clients: List[MCPClient] = []
        self.tools: List[tools_list_details] = []
        self.tool_dict:dict[str, MCPClient] = {}

    def load_servers(self, server_file:str)->None:
        """Load the server file which contains MCP server details"""
        with open(server_file, "r") as f:
            server_details = yaml.safe_load(f)
        logger.info(f"reading the config file {server_file}")
        for server in server_details["servers"]:
            self._add_server(**server)

    def _add_server(self, server_name:str, server_url:str, server_api_key:str, description:str=None, author:str=None, version:str=None,  server_type:str=None):
        """Add the server to the client manager"""
        client = MCPClient(server_name=server_name, server_url=server_url, server_api_key=server_api_key, author=author, description=description, version=version, server_type=server_type)
        self.clients.append(client)
        logger.info(f"added server: {self.clients}")

    async def connect_to_all_servers(self)->None:
        """Connect to all the servers in mcpserver.yaml"""
        for client in self.clients:
            await client.connect_sse_client()
        logger.info("sse connect established")
        #store all the connections in the pydantic format in p_model_type
        for client in self.clients:
            self.tools.extend(client.all_tools)

            for tool in client.all_tools:
                logger.info(f"client.all_tools: {tool}")
                self.tool_dict[f'{tool["service_name"]}00_{tool["tool_name"]}'] = client# create a dict key with server name, tool name version and author so that it can be distinguishable for the client.
            logger.info(f"Third Party MCP tools across all servers: {self.tool_dict}")

    def get_tool(self):
        """Get the tool from the client manager"""
        return self.tools

    async def process_tool_call(self, tool_calls:List[ChatCompletionMessageToolCall]) -> List[Dict[str, Any]]:
        """Process the tool call and return the response"""
        responses = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name.split("00_")[1]
            tool_args = json.loads(tool_call.function.arguments)
            client = self.tool_dict.get(tool_call.function.name)
            logger.info(f"Selected details process tool call: {client} {tool_call} {tool_call.function.name} {tool_name} {tool_args}")
            if client:
                # response = await client.call_tool(tool_name, tool_args)
                response = await client.call_tool(tool_name=tool_name, tool_args=tool_args)
                # logger.info(f"response from the tool: {response}")
                responses.append(response)
            else:
                logger.error(f"Tool {tool_name} not found in any client")
        return responses
        
    async def cleanup(self):
        """Cleanup all clients"""
        # Clean up all clients in reverse order
        for client in reversed(self.clients):
            await client.cleanup() 
