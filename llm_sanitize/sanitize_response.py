from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import settings
from utils.logger import logger 
from typing import Dict
from llm_sanitize.prompts import tool_posion_attack_sanitize

llm = ChatOpenAI(model=settings.MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY)

async def response_sanitize(user_query: Dict, response:Dict)->Dict:
    """sanitize the response from mcp central"""
    logger.info(f"request to sanitize: {user_query}, {response}")
    prompt = ChatPromptTemplate.from_template(tool_posion_attack_sanitize)
    chain = prompt |llm
    logger.info(f"chain: {chain}")
    result = await chain.ainvoke({"user_query":user_query,"chat_context":response})
    logger.info(f"response from the LLM: {result} ")
    return result