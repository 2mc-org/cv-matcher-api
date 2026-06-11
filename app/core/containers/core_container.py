from typing import Annotated

import socketio
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends
from redis.asyncio import Redis

from app.core.db.database import get_session
from app.core.db.session_manager import sessionmanager
from app.core.environments import environments
from app.core.socket.server import get_sio
from app.graph.core.containers.graph_packages_paths import GRAPH_PACKAGES_PATHS


class CoreContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.cv.router",
        ],
        packages=[
            *GRAPH_PACKAGES_PATHS,
        ],
    )

    # Gateways
    db = providers.Object(sessionmanager)
    session = providers.Resource(get_session)
    redis = providers.Singleton(
        Redis.from_url,
        environments.REDIS_URL,
        decode_responses=True,
    )
    sio = providers.Callable(get_sio)


# Dependencies
SioDependency = Annotated[
    socketio.AsyncServer, Depends(Provide[CoreContainer.sio])
]
