import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from starlette.requests import Request

from app.uniprot.uniprot import uniprot_route

instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
)

app = FastAPI(
    docs_url="/",
    title="3D Beacons HUB API",
    description="The 3D-Beacons Network provides unified programmatic access to "
    "experimentally determined and predicted structure models.",
    redoc_url=None,
    version=1.0,
)
app.include_router(uniprot_route, prefix="/uniprot")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware)

instrumentator.add(
    metrics.latency(
        buckets=(
            1,
            2,
            3,
        )
    )
)
instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=False, should_gzip=True)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def load_configs():
    from app.config import load_data_file

    load_data_file()


@app.on_event("shutdown")
async def clear_config_caches():
    from app.config import get_providers, load_data_file, read_data_file

    read_data_file.cache_clear()
    load_data_file.cache_clear()
    get_providers.cache_clear()
