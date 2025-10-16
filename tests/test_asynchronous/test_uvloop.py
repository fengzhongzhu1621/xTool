import asyncio

from xTool.asynchronous.aiomisc import load_uvloop


async def main():
    await asyncio.sleep(1)


def test_load_uvloop():
    load_uvloop()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
