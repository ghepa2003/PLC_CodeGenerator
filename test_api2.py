import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="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",
    base_url="https://openrouter.io/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "PLC Code Generator"
    }
)

async def test():
    try:
        res = await client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": "Hello"}],
        )
        print("SUCCESS:", res.choices[0].message.content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
