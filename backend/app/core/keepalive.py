import asyncio
import httpx
import os

async def keep_alive():
    url = os.getenv("https://iteragen.onrender.com", "")
    if not url:
        return
    await asyncio.sleep(60)
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(f"{url}/health", timeout=10)
                print("Keep-alive ping sent")
        except:
            pass
        await asyncio.sleep(540)
