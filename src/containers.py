from dishka import make_async_container

from src.app.entrypoints.dependencies import UseCaseProvider
from src.core.settings import Settings, settings
from src.infra.entrypoints.dependencies import InfraProvider

container = make_async_container(
    InfraProvider(),
    UseCaseProvider(),
    context={
        Settings: settings,
    },
)
