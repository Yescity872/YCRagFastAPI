import asyncio
from typing import Any, Callable


async def run_blocking(func: Callable[..., Any], *args, timeout: float | None = None, **kwargs) -> Any:
    """Run a blocking function in a worker thread without blocking the event loop.

    Args:
        func: Callable to run in a thread.
        *args, **kwargs: Arguments for the callable.
        timeout: Optional seconds to wait before raising TimeoutError.

    Returns:
        The result of func(*args, **kwargs).
    """
    task = asyncio.to_thread(func, *args, **kwargs)
    return await asyncio.wait_for(task, timeout=timeout) if timeout else await task
