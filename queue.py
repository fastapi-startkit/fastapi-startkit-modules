from __future__ import annotations

import asyncio
import importlib
import inspect
import json
import time
import uuid
from abc import ABC, abstractmethod
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Pool strategies
# ---------------------------------------------------------------------------

class Pool(ABC):
    """Abstract base class that all pool strategies must implement."""

    @abstractmethod
    def submit(self, payload: dict) -> None:
        """Dispatch a serialised job payload for execution."""

    def shutdown(self) -> None:
        """Clean up resources. Override when the pool holds an executor."""

    @staticmethod
    def parse(payload: dict) -> tuple[str, str]:
        """Return (fully-qualified class path, method name) from a payload."""
        return payload["class"], payload["method"]

    @staticmethod
    def resolve_and_call(payload: dict) -> None:
        """Deserialise a payload, instantiate the job class, and call its method."""
        class_path, method = Pool.parse(payload)
        module_name, class_name = class_path.rsplit(".", 1)
        cls = getattr(importlib.import_module(module_name), class_name)
        result = getattr(cls(**payload.get("data", {})), method)()
        if asyncio.iscoroutine(result):
            asyncio.run(result)


class ThreadPool(Pool):
    """Each job runs in a worker thread; async jobs get their own event loop."""

    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, payload: dict) -> None:
        self._executor.submit(Pool.resolve_and_call, payload)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)


class AsyncPool(Pool):
    """Jobs run on the current event loop as asyncio Tasks."""

    def __init__(self) -> None:
        self._tasks: list[asyncio.Task] = []

    def submit(self, payload: dict) -> None:
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._run(payload))
        self._tasks.append(task)

    @staticmethod
    async def _run(payload: dict) -> None:
        class_path, method = Pool.parse(payload)
        module_name, class_name = class_path.rsplit(".", 1)
        cls = getattr(importlib.import_module(module_name), class_name)
        result = getattr(cls(**payload.get("data", {})), method)()
        if asyncio.iscoroutine(result):
            await result

    async def drain(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()


class ProcessPool(Pool):
    """Each job runs in a separate OS process via asyncio.run() internally."""

    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ProcessPoolExecutor(max_workers=max_workers)

    def submit(self, payload: dict) -> None:
        # Pool.resolve_and_call is a static method on an importable class — picklable
        self._executor.submit(Pool.resolve_and_call, payload)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

class Queue:
    def __init__(self) -> None:
        self._store: deque[dict] = deque()
        self.failed: list[dict] = []

    def push(self, job: "Job") -> None:
        self._store.append(job.payload())

    def pop(self) -> dict | None:
        return self._store.popleft() if self._store else None

    def size(self) -> int:
        return len(self._store)

    @staticmethod
    def fire(payload: dict) -> None:
        Pool.resolve_and_call(payload)

class DatabaseQueue(Queue):
    """Database-backed queue. Persists jobs to a `jobs` table via SQLAlchemy."""

    def __init__(self, connection_name: str = "default") -> None:
        super().__init__()
        self._connection_name = connection_name
        self._db: Any = None   # inject an AsyncSession / connection here

    # -- public ---------------------------------------------------------------

    def push(self, job: "Job", queue: str = "default", delay: int = 0) -> str:
        payload = self.create_payload(job, queue)
        return self.push_to_database(queue, payload, delay, attempts=0)

    def later(self, job: "Job", delay: int, queue: str = "default") -> str:
        """Push a job with a delay (seconds from now)."""
        return self.push(job, queue=queue, delay=delay)

    # -- payload --------------------------------------------------------------

    def create_payload(self, job: "Job", queue: str = "default") -> dict:
        class_path = f"{job.__class__.__module__}.{job.__class__.__name__}"
        return {
            "uuid":          str(uuid.uuid4()),
            "display_name":  self._get_display_name(job),
            "job":           class_path,
            "max_tries":     getattr(job, "tries", None),
            "max_exceptions":getattr(job, "max_exceptions", None),
            "fail_on_timeout":getattr(job, "fail_on_timeout", False),
            "backoff":       self._get_backoff(job),
            "timeout":       getattr(job, "timeout", None),
            "retry_until":   self._get_expiration(job),
            "data": {
                "command_name": class_path,
                "command":      job.payload(),
                "batch_id":     getattr(job, "batch_id", None),
            },
            "created_at":    int(datetime.now(timezone.utc).timestamp()),
        }

    # -- database interaction -------------------------------------------------

    def push_to_database(
        self, queue: str, payload: dict, delay: int, attempts: int
    ) -> str:
        available_at = int(datetime.now(timezone.utc).timestamp()) + delay

        # Example row — replace with: await JobModel.create(...)
        row = {
            "uuid":         payload["uuid"],
            "queue":        queue,
            "payload":      payload,
            "attempts":     attempts,
            "available_at": available_at,
            "created_at":   payload["created_at"],
        }
        _ = row   # placeholder until DB model is wired in
        return payload["uuid"]

    def pop(self) -> dict | None:
        """
        Fetch the next available job from the database.

        Override with: SELECT ... WHERE available_at <= NOW() ORDER BY id LIMIT 1.
        Falls back to in-memory store when no DB is wired.
        """
        return super().pop()

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _get_display_name(job: "Job") -> str:
        return job.__class__.__name__

    @staticmethod
    def _get_backoff(job: "Job") -> int | list[int] | None:
        return getattr(job, "backoff", None)

    @staticmethod
    def _get_expiration(job: "Job") -> int | None:
        retry_until = getattr(job, "retry_until", None)
        if callable(retry_until):
            return int(retry_until().timestamp())
        return int(retry_until.timestamp()) if retry_until else None

class RedisQueue(Queue):
    """Redis-backed queue (lpush / brpop)."""

    def __init__(self, connection_name: str = "default") -> None:
        super().__init__()
        self._connection_name = connection_name
        self._client: Any = None   # inject a redis.Redis / aioredis client here

    def push(self, job: "Job") -> None:
        if self._client:
            import json
            self._client.lpush(self._connection_name, json.dumps(job.payload()))
        else:
            super().push(job)   # fall back to in-memory while not connected

    def pop(self) -> dict | None:
        if self._client:
            import json
            result = self._client.brpop(self._connection_name, timeout=1)
            return json.loads(result[1]) if result else None
        return super().pop()


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

class Worker:
    def __init__(
        self,
        queue: Queue,
        pool: Pool | None = None,
        max_jobs: int | None = None,
    ) -> None:
        self._queue = queue
        self._pool = pool or ThreadPool()
        self._max_jobs = max_jobs   # None = run forever (real daemon)

    def daemon(self) -> None:
        start_time, job_processed = time.time(), 0

        while True:
            job = self._queue.pop()

            if job is not None:                  # fixed: was `if job None:`
                job_processed += 1
                self.run_job(job)

            if self._max_jobs and job_processed >= self._max_jobs:
                break

            if job is None:
                time.sleep(0.05)

        self._pool.shutdown()

        elapsed = time.time() - start_time
        print(f"[worker] processed {job_processed} job(s) in {elapsed:.3f}s")

    def run_job(self, job: dict) -> None:        # fixed: removed unused `connection_name` param
        try:
            self.process(job)
        except Exception as e:
            self.report(e, job)
            self.stop_worker_if_connection_lost(e)

    def process(self, job: dict) -> None:
        self._pool.submit(job)                   # fixed: exceptions now propagate out of process()

    def report(self, e: Exception, job: dict | None = None) -> None:
        label = job.get("class", "unknown") if job else "unknown"
        print(f"[worker] job failed — {label}: {e}")
        if job:
            self._queue.failed.append({"payload": job, "error": str(e)})

    @staticmethod
    def stop_worker_if_connection_lost(e: Exception) -> None:
        connection_errors = (ConnectionError, OSError)
        if isinstance(e, connection_errors):
            raise SystemExit(f"[worker] stopping — connection lost: {e}")


# ---------------------------------------------------------------------------
# Base Job
# ---------------------------------------------------------------------------

class Job:
    def payload(self) -> dict:
        return {
            "class": f"{self.__class__.__module__}.{self.__class__.__name__}",
            "method": "handle",
            "data": self._data(),
        }

    def _data(self) -> dict:
        """Serialise all constructor arguments automatically from instance attributes."""
        params = inspect.signature(self.__class__.__init__).parameters
        return {
            name: getattr(self, name)
            for name in params
            if name != "self" and hasattr(self, name)
        }

    def handle(self) -> None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# EmailQueue  (specialised queue for mail jobs)
# ---------------------------------------------------------------------------

class EmailQueue(Queue):
    async def handle(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Demo  (python queue.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # -- define a quick inline job for the demo ------------------------------
    class WelcomeEmail(Job):
        def __init__(self, email: str, name: str = "there") -> None:
            self.email = email
            self.name = name

        def handle(self) -> None:
            print(f"  [job] WelcomeEmail → to={self.email}, name={self.name}")

    # -------------------------------------------------------------------------

    q = Queue()
    q.push(WelcomeEmail(email="alice@example.com", name="Alice"))
    q.push(WelcomeEmail(email="bob@example.com"))

    print(f"[queue] {q.size()} job(s) queued\n")

    # uv run artisan queue:work --pool=thread (default)
    worker = Worker(q, pool=ThreadPool(max_workers=2), max_jobs=2)
    worker.daemon()
