import asyncio
import threading
from toolbox.utils import err, warn, exc


def get_or_create_event_loop():
    try:
        loop = asyncio.get_event_loop()
        return loop
    except RuntimeError:
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
        loop = get_or_create_event_loop()
        return loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        err(f"Failed to run event loop: {e}")
        warn(exc())


def run_async_bg_tasks(*coro_or_future):
    try:

        def run_in_thread(loop, tasks):
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(asyncio.gather(*tasks))
            finally:
                loop.close()

        loop = asyncio.new_event_loop()
        tasks = [asyncio.ensure_future(task, loop=loop) for task in coro_or_future]
        thread = threading.Thread(target=run_in_thread, args=(loop, tasks))
        thread.start()
        return tasks
    except Exception as e:
        err(f"Failed to schedule background task(s): {e}")
        warn(exc())
        return None


def safe_run(func, default=None):
    try:
        return func()
    except:
        warn(exc())
        return default


async def async_safe_run(func, default=None):
    try:
        return func()
    except:
        warn(exc())
        return default
