from os import environ

import aiohttp
import pytest
from custom_components.tapo_p100.discover import discover
from custom_components.tapo_p100.p100 import P100
from dotenv import load_dotenv

pytestmark = pytest.mark.asyncio
load_dotenv()


@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
async def p100(session):
    return P100(
        address=discover()["ip"],
        email=environ["TAPO_EMAIL"],
        password=environ["TAPO_PASSWORD"],
        session=session,
    )


async def test_device_info(p100: P100):
    info = await p100.device_info()
    print(info)
