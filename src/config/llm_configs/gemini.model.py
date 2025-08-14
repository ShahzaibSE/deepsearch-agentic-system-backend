from dotenv import load_dotenv
import os
from agents import AsyncOpenAI
from config import BaseModelConfig


class GeminiConfig(BaseModelConfig):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = AsyncOpenAI(api_key=self.api_key)

    # async def get_chat_completion(self, messages: list[dict]) -> str:
    #     try:
    #         response = await self.client.chat.completions.create(
    #             model="gemini-pro",
    #             messages=messages
    #         )
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         print(f"Error getting Gemini chat completion: {e}")
    #         return ""