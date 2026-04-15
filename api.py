import sys
from fastapi import FastAPI
from app.routes import router
from app.manager import browser_manager
from contextlib import asynccontextmanager
from toolbox.api import logger_middleware, init_scalar_docs, run_server
from toolbox.utils import get_env


ENV = get_env("ENV", "PROD", verbose=1)
HOT_RELOAD = False if ENV == "PROD" else get_env("HOT_RELOAD", False, verbose=1)
LOG_REQUESTS = get_env("LOG_REQUESTS", False, verbose=1)
LOG_RESPONSE = get_env("LOG_RESPONSE", False, verbose=1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await browser_manager.close()


app = FastAPI(
    title="Impresario",
    version="1.0",
    docs_url=None,
    lifespan=lifespan,
)

app.include_router(router)


if ENV == "DEV" or LOG_REQUESTS or LOG_RESPONSE:
    logger_middleware(app, ENV, LOG_REQUESTS, LOG_RESPONSE)


init_scalar_docs(
    app,
    title="Impresario API Reference",
    authentication={"preferredSecurityScheme": "ApiKeyAuth"},
    persist_auth=True,
)


sys.stdout.reconfigure(line_buffering=True)


if __name__ == "__main__":
    run_server("api:app", ENV, port=8077, hot_reload=HOT_RELOAD)
