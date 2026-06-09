import asyncio
import httpx
from config import GOOGLE_API_KEY
async def test():
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            params={"key": GOOGLE_API_KEY},
            json={
                "contents": [{"parts": [{"text": "Hello" * 1000}]}],
                "systemInstruction": {"parts": [{"text": "You are a helpful assistant."}]}
            }
        )
        print("Status:", res.status_code)
        print("Body:", res.text)
asyncio.run(test())
