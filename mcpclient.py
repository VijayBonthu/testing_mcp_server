from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from utils.logger import logger
from p_model_type import tools_list_details
from contextlib import AsyncExitStack

class MCPClient:
    def __init__(self, server_name:str, server_url:str, server_api_key:str=None, description:str=None, author:str=None, version:str=None, server_type:str=None)->None:
        self.server_name = server_name
        # self.transport = transport
        self.server_url = server_url
        self.server_api_key = server_api_key
        self.description = description
        self.author = author
        self.version = version
        self.server_type = server_type
        self._stack = AsyncExitStack()
        logger.info(f"creating client for {self.server_name} {self.server_url} {self.server_api_key} {self.description} {self.author} {self.version} {self.server_type}")

        self.session:Optional[ClientSession] = None
        self.all_tools:Optional[List[Dict[str,Any]]] = None
        self._streams_context = None
        self._session_context = None
        
    async def connect_sse_client(self)->None:
        """connnect to the sse client"""
        # async with sse_client(url=self.server_url,
        #                       headers={"Authorization": f"Bearer {self.server_api_key}"}) as (recv, send):
        # async with sse_client(url=self.server_url) as (recv, send):
        #     async with ClientSession(recv, send) as self.session:
        try:
            # if self.transport == 'sse':
            #     self._streams_context = sse_client(url=self.server_url,
            #                 headers={"Authorization": f"Bearer {self.server_api_key}"} if self.server_api_key else {})
            # elif self.transport == "stdio":
            #     self._streams_context = stdio_client()
            # else:
            #     raise ValueError(f"unknown transport {self.transport} can only be 'sse' for connect to api though llm or 'stdio' for apps like cursor or windsurf")
            self._streams_context = sse_client(url=self.server_url,
                            headers={"Authorization": f"Bearer {self.server_api_key}"} if self.server_api_key else {})
            streams = await self._streams_context.__aenter__()
            self._session_context = ClientSession(*streams)
            self.session = await self._session_context.__aenter__()
            await self.session.initialize()
            # logger.info(f"connected to the server {self.transport} {self.server_name} {self.server_url}")
            logger.info(f"session initialization done {self.server_name} {self.server_url}")
            logger.info(f"listing tools initialized")
            tools_list = await self.session.list_tools()
            tools = tools_list.tools

            self.all_tools = [
                tools_list_details(
                    service_name = self.server_name,
                    service_url = self.server_url,
                    sevice_description = self.description,
                    service_author = self.author,
                    service_version = self.version,
                    service_type = self.server_type,
                    tool_name=tool.name,
                    tool_description=tool.description,
                    tool_parameters=tool.inputSchema
                ).model_dump()
                for tool in tools
            ]
            logger.info(f"ALL third party MCP server tools: {self.all_tools}")
        except Exception as e:
            logger.error(f"Failed to connect to SSE client for {self.server_name}: {e}")
            raise

    async def call_tool(self, tool_name:str, tool_args)->Dict[str, Any]:
        """call the tool with the given name and args"""
        logger.info(f"inside the call_tool method in mcpclient.py {self.session} {tool_name} {tool_args}")
        if self.session is None:
            raise ValueError("session not initialized. Please call connect_sse_clent() first")
        if self.all_tools is None:
            raise ValueError("No tools available for the url provided")
        try:
            response = await self.session.call_tool(name=tool_name, arguments=tool_args)
            logger.info(f"response from call_tool: {response}")
            return response
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise

    async def cleanup(self):
        """Properly clean up the session and streams"""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
            if self._streams_context:
                await self._streams_context.__aexit__(None, None, None)
            logger.info(f"Cleaned up client for {self.server_name}")
        except Exception as e:
            logger.error(f"Error during cleanup for {self.server_name}: {e}")
            