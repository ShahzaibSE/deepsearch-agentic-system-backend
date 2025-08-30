import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, Request, Response, HTTPException
import asyncio
from aiohttp import ClientSession

#Agents
from config._agents._web_search_agent import WebSearchAgent
from config._agents._base_agent import BaseAgentBuilder

router = APIRouter()

@router.post("/web-search")
def web_search(request: Request, response: Response):
    return "Web Search Orchestrator test response"