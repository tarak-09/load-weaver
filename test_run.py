import asyncio
from omniload.core import LoadGenerator
async def main():
    gen = LoadGenerator("http://127.0.0.1:8080/", 1, 1, "POST", {"X-Test": "1"}, "data")
    res = await gen.run()
    print("Success")
asyncio.run(main())
