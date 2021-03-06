import time

from fastapi import FastAPI
from starlette.requests import Request

from app.uniprot.uniprot import uniprot_route

app = FastAPI()
app.include_router(uniprot_route, prefix="/uniprot")


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
