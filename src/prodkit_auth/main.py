from fastapi import FastAPI

from prodkit_auth.config import get_settings, validate_production_settings
from prodkit_auth.routes import router


def create_app() -> FastAPI:
    validate_production_settings(get_settings())
    app = FastAPI(
        title="FastAPI Auth Production Kit",
        version="0.1.0",
        description="Runnable FastAPI auth starter with production decision guides.",
    )
    app.include_router(router)
    return app


app = create_app()
