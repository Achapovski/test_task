from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.app.entrypoints.routes.v1 import router
from src.app.exceptions.registrator import register_exception_handlers
from src.bootstrap import lifespan
from src.containers import container

app = FastAPI(
    title="Payment Service",
    description="Async payment microservice",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router=router)

register_exception_handlers(app=app)
setup_dishka(container=container, app=app)
