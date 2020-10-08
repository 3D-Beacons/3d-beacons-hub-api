import asyncio
from typing import Any, List, Optional

from fastapi.params import Path, Query
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.config import get_base_service_url, get_services
from app.uniprot.schema import Result, Structure, UniProtEntry
from app.utils import request_get_stub
from app import logger

uniprot_route = APIRouter()


@uniprot_route.get(
    "/{qualifier}.json", status_code=status.HTTP_200_OK, response_model=Result
)
async def get_uniprot(
    qualifier: Any = Path(
        ..., description="UniProtKB accession number (AC) or entry name (ID)"
    ),
    provider: Optional[Any] = Query(
        None, enum=["swissmodel", "genome3d", "foldx", "pdb"]
    ),
    template: Optional[Any] = Query(
        None,
        description="Template is 4 letter PDB code, or 4 letter code with "
        "assembly ID and chain for SMTL entries",
    ),
    res_range: Optional[Any] = Query(
        None,
        description="Specify a UniProt sequence residue range",
        pattern="^[0-9]+-[0-9]+$",
        alias="range",
    ),
):
    """ Returns experimental and theoretical models for a UniProt accession or entry name

    Args:
        qualifier (str): UniProtKB accession number (AC) or entry name (ID).
        provider (str, optional): Data provider
        template (str, optional): 4 letter PDB code, or 4 letter code with assembly ID
        and chain for SMTL entries
        res_range (str, optional): Residue range

    Returns:
        Result: A Result object with experimental and theoretical models.
    """

    services = get_services(service_type="uniprot", provider=provider)
    calls = []

    for service in services:
        base_url = get_base_service_url(service["provider"])
        final_url = base_url + service["accessPoint"] + f"{qualifier}.json?"

        if res_range:
            final_url = f"{final_url}range={res_range}"

        calls.append(final_url)

    tasks = [asyncio.create_task(request_get_stub(call)) for call in calls]
    result = await asyncio.gather(*tasks)
    final_result = [x.json() for x in result if x and x.status_code == 200]

    if not final_result:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    final_structures: List[Structure] = []
    uniprot_entry: UniProtEntry = UniProtEntry(**final_result[0]["uniprot_entry"])

    for item in final_result:
        final_structures.extend(item["structures"])

    api_result: Result = Result(
        **{"uniprot_entry": uniprot_entry, "structures": final_structures}
    )

    return api_result
