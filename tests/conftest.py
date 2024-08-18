import subprocess
import time

import httpx
import pytest


@pytest.fixture(scope="session")
def run_server():
    redis_process = subprocess.Popen(["redis-server"])
    rabbitmq_process = subprocess.Popen(["rabbitmq-server"])

    time.sleep(2)

    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    )
    time.sleep(5)
    yield

    process.terminate()
    process.wait()

    redis_process.terminate()
    redis_process.wait()

    rabbitmq_process.terminate()
    rabbitmq_process.wait()


@pytest.fixture
async def api_client(run_server):
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        yield client


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
