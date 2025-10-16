import asyncio

from xTool.servers.tracer import MemoryTracer


def test_meory_tracer():
    loop = asyncio.get_event_loop()

    service = MemoryTracer(interval=1, top_results=5)

    loop.run_until_complete(service.start())

    async def stop():
        await asyncio.sleep(2)

    loop.run_until_complete(
        asyncio.wait_for(stop(), timeout=3),
    )
    loop.close()
