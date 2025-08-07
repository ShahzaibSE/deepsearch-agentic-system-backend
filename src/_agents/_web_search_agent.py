from agents import Agent, AsyncOpenAI, ModelSettings, AsyncOpenAI, set_tracing_disabled
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).resolve().parent / ".env")

path = os.getenv('GEMINI_API_KEY')
print(path)

client = AsyncOpenAI(
    
)

