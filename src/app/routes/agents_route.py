import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, Request, Response, HTTPException
import asyncio
from aiohttp import ClientSession

#Agents
from config._agents.web_search_agent import WebSearchAgent
from config._agents.base_agent import BaseAgentBuilder
from config.security import rate_limit, ip_whitelist


router = APIRouter()

@router.post("/web-search")
@rate_limit(requests_per_minute=10, requests_ip_whitelist=["127.0.0.1"])
def web_search(request: Request, response: Response):



    return "Web Search Orchestrator test response"