from mcp.server.fastmcp import FastMCP, Context
from starlette.applications import Starlette
from starlette.routing import Mount
from startlette import create_starlette_app
import uvicorn
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import urllib.parse
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import time
import re

mcp = FastMCP('add server')

app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app())
    ]
)

@mcp.tool()
async def add(a:int, b:int)-> int:
    """Add Two Numbers"""
    print("🔔 add() called with", a, b)
    return a + b

if __name__=="__main__":
    starlette_app = create_starlette_app(
        mcp_server=mcp._mcp_server, api_key=None,debug=True
    )
    uvicorn.run(starlette_app, host='127.0.0.1',port=5100)
