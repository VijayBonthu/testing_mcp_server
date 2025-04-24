from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.routing import Route,Mount

def create_starlette_app(
        mcp_server:Server, *, api_key:str, debug:bool=False
) -> Starlette:
    """Create starlette server that can provide with sse"""

    sse = SseServerTransport("/messages/")
    async def handle_sse(request:Request)->None:
        if "Authorization" in request.headers:
            if request.headers["Authoriation"]!= f"Bearer {api_key}":
                raise HTTPException(status_code=401, detail=f"Invalid API Key")
            
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        
    )