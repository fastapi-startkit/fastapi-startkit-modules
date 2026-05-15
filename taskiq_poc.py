import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, List, Optional, Union, Type, TypeVar
from taskiq import AsyncBroker, InMemoryBroker, TaskiqResult

# --- Mocking external dependencies for the PoC ---

class NowMock:
    """Mock for pendulum.now() or similar"""
    def __init__(self, dt: datetime = None):
        self.dt = dt or datetime.now()
    
    def add(self, minutes: int = 0, seconds: int = 0) -> datetime:
        return self.dt + timedelta(minutes=minutes, seconds=seconds)

def now():
    return NowMock()

# --- The Core Logic ---

T = TypeVar("T", bound="Queue")

class Queue:
    """
    Base class for Taskiq tasks with a class-based syntax.
    """
    queue: str = 'default'
    timeout: int = 60
    max_exceptions: int = 3
    tries: int | None = None
    rate_limit: str | None = None
    backoff: int | list[int] = 5

    _broker: AsyncBroker = None
    _taskiq_task = None


    @classmethod
    def bind(cls, broker: AsyncBroker):
        """
        Registers this class as a task in the given broker.
        """
        cls._broker = broker

        async def _task_runner(*args, **kwargs):
            # 1. Instantiate the class on the worker side
            instance = cls(*args, **kwargs)
            # 2. Execute the handle method
            return await instance.handle()

        # Register the task with proper labels so taskiq respects them
        # This ensures that 'timeout', 'max_retry', etc. are actually used by the broker.
        cls._taskiq_task = broker.register_task(
            _task_runner,
            task_name=f"{cls.__module__}.{cls.__name__}",
            queue_name=cls.queue,
        ).with_labels(
            timeout=cls.timeout,
            max_retry=cls.max_exceptions,
            backoff=cls.backoff,
            rate_limit=cls.rate_limit,
        )
        
        print(f"Registered task: {cls.__name__} on queue: {cls.queue}")

    @classmethod
    async def dispatch(cls, *args, **kwargs):
        """
        Dispatches the task to the broker using the class itself.
        """
        if not cls._taskiq_task:
            raise RuntimeError(
                f"Task {cls.__name__} is not bound to a broker. "
                "Call ClassifyTask.bind(broker) first."
            )

        print(f"Dispatching {cls.__name__} with args: {args} {kwargs}")
        
        # Send the arguments directly to the taskiq task
        return await cls._taskiq_task.kiq(*args, **kwargs)

    async def handle(self):
        """
        The actual logic to be executed by the worker.
        """
        raise NotImplementedError("Subclasses must implement the handle() method.")


# --- The Requested POC Implementation ---

class ClassifyTask(Queue):
    queue: str = 'default'
    timeout: int = 60  # Default timeout in seconds
    max_exceptions: int = 3  # Maximum number of exceptions before task is marked as failed

    tries: int | None = None
    rate_limit: str | None = '20/m'
    backoff: int | list[int] = 5
    
    @property
    def retry_until(self):
        return now().add(minutes=1)
    
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def handle(self):
        print(f"[Worker] Classifying data for user_id: {self.user_id}")
        print(f"[Worker] Task settings: queue={self.queue}, timeout={self.timeout}")
        # Simulate some work
        await asyncio.sleep(0.1)
        print(f"[Worker] Finished processing for user_id: {self.user_id}")


# --- Running the POC ---

async def main():
    # 1. Setup a broker (using InMemoryBroker for testing)
    broker = InMemoryBroker()
    
    # 2. Bind the task class to the broker
    # In a real app, you might automate this for all Queue subclasses
    ClassifyTask.bind(broker)

    # 3. Startup the broker (simulating worker/client initialization)
    await broker.startup()

    # 4. Dispatch a task
    # This now uses the class method directly
    handle = await ClassifyTask.dispatch(user_id=42)
    
    print(f"Task dispatched! Task ID: {handle.task_id}")

    # 5. Wait for the result (since it's an InMemoryBroker, it runs immediately)
    result = await handle.wait_result(timeout=2)
    print(f"Task result: {result.return_value}")

    await broker.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
