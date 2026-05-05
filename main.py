import asyncio
from ricochet.controller import Game


async def main():
    await Game().run()


asyncio.run(main())
