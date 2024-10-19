import asyncio
from toolbox.utils import err, warn, exc


def create_and_set_event_loop():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
    except Exception as e:
        err(f"Failed to create event loop: {e}")
        warn(exc())
    return None


def run_async_tasks(*tasks):
    try:
        loop = create_and_set_event_loop()
        return loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        err(f"Failed to run event loop: {e}")
        warn(exc())
