import httpx
import asyncio

async def t():
    res = await httpx.AsyncClient().post(
        'https://openrouter.io/api/v1/chat/completions',
        headers={
            'Authorization': 'Bearer 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',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'PLC Code Generator'
        },
        json={'model': 'meta-llama/llama-3.3-70b-instruct:free', 'messages': [{'role':'user', 'content':'hello'}]}
    )
    print(res.status_code, res.text)

asyncio.run(t())
