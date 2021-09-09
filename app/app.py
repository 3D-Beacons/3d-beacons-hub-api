import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.requests import Request

from app.uniprot.uniprot import uniprot_route

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
