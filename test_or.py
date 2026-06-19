import asyncio
import time
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key='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',
    base_url='https://openrouter.ai/api/v1',
    default_headers={'HTTP-Referer': 'https://test.com', 'X-Title': 'test'}
)

async def main():
    start = time.time()
    try:
        response = await client.chat.completions.create(
            model='qwen/qwen3-coder:free',
            messages=[{'role': 'user', 'content': 'hello'}],
            temperature=0.2
        )
        print(f"DONE in {time.time() - start:.2f}s:", response.choices[0].message.content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(main())
