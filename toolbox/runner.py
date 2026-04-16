import asyncio
import threading
from time import time
from toolbox.date import time_now
from toolbox.utils import printc
from toolbox.exceptions import ToolboxError, ToolboxWarning


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
            raise ToolboxError(f"Failed to create event loop: {e}")


def run_async_tasks(*tasks):
    try:
        loop = get_or_create_event_loop()
        results = loop.run_until_complete(asyncio.gather(*tasks))
        return results[0] if len(tasks) == 1 else results
    except Exception as e:
        raise ToolboxError(f"Failed to run event loop: {e}")


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
        return tasks[0] if len(tasks) == 1 else tasks
    except Exception as e:
        raise ToolboxError(f"Failed to schedule background task(s): {e}")


def safe_run(func, default=None):
    try:
        return func()
    except Exception as e:
        ToolboxWarning(f"Failed to safely run function: {func} [{e}]")
        return default


async def async_safe_run(func, default=None):
    try:
        return func()
    except Exception as e:
        ToolboxWarning(f"Failed to safely run async function: {func} [{e}]")
        return default


def timed_run(func, *args, **kwargs):
    exec_start = time()
    result = func(*args, **kwargs)
    exec_end = time()
    printc(
        f"[{time_now()}] {func.__name__}: completed in {exec_end - exec_start:.2f}s",
        "yellow",
    )
    return result
