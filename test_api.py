import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv("backend/.env")

client = AsyncOpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY", ""),
    base_url="https://openrouter.io/api/v1"
)

async def test():
    try:
        res = await client.chat.completions.create(
            model="anthropic/claude-3-5-sonnet",
            messages=[{"role": "user", "content": "ciao"}],
        )
        print("Success:", res.choices[0].message.content)
    except Exception as e:
        print("Error:", str(e))

asyncio.run(test())
