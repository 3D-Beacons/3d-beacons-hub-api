import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
from uvicorn.workers import UvicornWorker

from app import REDIS_URL
from app.annotations.annotations import annotations_route
from app.ensembl.ensembl import ensembl_route
from app.health.health import health_route
from app.sequence.sequence import sequence_route
from app.uniprot.uniprot import uniprot_route
from app.version import __version__ as schema_version

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
    contact={
        "name": "3D-Beacons Network",
        "url": "https://3dbeacons.org",
        "email": "pdbekb_help@ebi.ac.uk",
    },
    license_info={
        "name": "CC BY 4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    },
    redoc_url=None,
    version=schema_version,
)
app.include_router(uniprot_route, prefix="/uniprot")
app.include_router(ensembl_route, prefix="/ensembl")
app.include_router(sequence_route, prefix="/sequence")
app.include_router(annotations_route, prefix="/annotations")
app.include_router(health_route, prefix="/health")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware)

instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=False, should_gzip=False)


@app.middleware("http")
async def add_extra_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-3DBeacons-API-Version"] = schema_version
    return response


@app.on_event("startup")
async def load_configs():
    from app.config import load_data_file
    from worker.cache.redis_cache import RedisCache

    RedisCache.init_redis(REDIS_URL, "utf-8")
    load_data_file()


@app.on_event("shutdown")
async def clear_config_caches():
    from app.config import get_providers, load_data_file, read_data_file

    read_data_file.cache_clear()
    load_data_file.cache_clear()
    get_providers.cache_clear()


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {}
    root_path = os.environ.get("ROOT_PATH", "")
    if root_path:
        CONFIG_KWARGS.update({"root_path": root_path})


def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get("paths").items():
            for _, param in method_item.items():
                responses = param.get("responses")
                # remove 422 response, also can remove other status code
                if "422" in responses:
                    del responses["422"]
    return app.openapi_schema


app.openapi = custom_openapi
