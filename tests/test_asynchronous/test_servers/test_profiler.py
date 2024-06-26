import asyncio
import os
from pstats import Stats
from tempfile import NamedTemporaryFile

from xTool.servers.profiler import Profiler


async def test_profiler_start_stop():
    profiler = Profiler(interval=0.1, top_results=10)
    try:
        await profiler.start()
        await asyncio.sleep(0.5)
    finally:
        await profiler.stop()


async def test_profiler_dump():
    profiler = None
    path = NamedTemporaryFile(delete=False).name

    try:
        profiler = Profiler(
            interval=0.1,
            top_results=10,
            path=path,
        )
        await profiler.start()

        # Not enough sleep till next update
        await asyncio.sleep(0.2)
        stats1 = Stats(path)

        await asyncio.sleep(0.25)
        stats2 = Stats(path)
        assert stats1.stats != stats2.stats

        # Enough sleep till next update
        await asyncio.sleep(0.3)
        stats3 = Stats(path)

        # Getting updated dump
        assert stats2.stats != stats3.stats

    finally:
        if profiler:
            await profiler.stop()
        os.remove(path)
