from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class tools_list_details(BaseModel):
    service_name:str = Field(..., description="name of the mcp server")
    service_url:str = Field(..., description="url of the mcp server")
    sevice_description:str = Field(..., description="description of the server")
    service_author:str = Field(..., description="name of the server author")
    service_version:str = Field(..., description="server version")
    service_type:str = Field(..., description="Type of the server")
    tool_name: str = Field(..., description="name of the tool")
    tool_description: str = Field(..., description="description of the tool")
    tool_parameters: Optional[Dict] = Field(None, description="parameters of the tool")