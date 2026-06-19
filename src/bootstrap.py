from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.containers import container


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: F841
    await container.get(async_sessionmaker)

    yield

    await container.close()
