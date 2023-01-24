from typing import Any, List, Optional

import pydantic
from fastapi.params import Path, Query
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app import logger
from app.config import get_base_service_url, get_services
from app.constants import TEMPLATE_DESC, UNIPROT_QUAL_DESC, UNP_CHECKSUM_DESC
from app.uniprot.helper import (
    filter_on_checksum,
    get_first_entry_with_checksum,
    get_list_of_uniprot_summary_helper,
    get_uniprot_summary_helper,
)
from app.uniprot.schema import (
    AccessionListRequest,
    Detailed,
    UniprotDetails,
    UniprotEntry,
    UniprotSummary,
)
from app.utils import clean_args, get_final_service_url, send_async_requests

uniprot_route = APIRouter()


@uniprot_route.get(
    "/summary/{qualifier}.json",
    status_code=status.HTTP_200_OK,
    response_model=UniprotSummary,
    response_model_exclude_unset=True,
    tags=["UniProt"],
)
async def get_uniprot_summary(
    qualifier: Any = Path(..., description=UNIPROT_QUAL_DESC, example="P38398"),
    provider: Optional[Any] = Query(
        None, enum=[x["provider"] for x in get_services("summary")]
    ),
    template: Optional[Any] = Query(
        None,
        description=TEMPLATE_DESC,
    ),
    res_range: Optional[Any] = Query(
        None,
        description="Specify a UniProt sequence residue range",
        pattern="^[0-9]+-[0-9]+$",
        alias="range",
    ),
    exclude_provider: Optional[str] = Query(
        None,
        description="Provider to exclude.",
        enum=[x["provider"] for x in get_services("summary")],
    ),
    uniprot_checksum: Optional[str] = Query(None, description=UNP_CHECKSUM_DESC),
):
    f"""Returns summary of experimental and theoretical models for a UniProt
    accession or entry name

    Args:
        qualifier (str): {UNIPROT_QUAL_DESC}
        provider (str, optional): Data provider
        template (str, optional): {TEMPLATE_DESC}
        res_range (str, optional): Residue range
        exclude_provider (str, optional): Provider to exclude
        uniport_checksum (str, optional): {UNP_CHECKSUM_DESC}

    Returns:
        Result: A Result summary object with experimental and theoretical models.
    """
    results = await get_uniprot_summary_helper(
        qualifier,
        provider,
        template,
        res_range,
        exclude_provider,
        uniprot_checksum,
    )

    if not results:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)
    else:
        return results


@uniprot_route.post(
    "/summary",
    status_code=status.HTTP_200_OK,
    response_model=List[UniprotSummary],
    response_model_exclude_unset=True,
    description="Returns summary of experimental and theoretical models for a "
    "list of UniProt accessions",
    tags=["UniProt"],
)
async def get_list_of_uniprot_summary(list_request: AccessionListRequest):
    """Returns summary of experimental and theoretical models for a list of UniProt
    accessions

    Args:
        list_request (AccessionListRequest): List of UniProt accession objects

    Returns:
        Result: A list of Result summary object with experimental and theoretical
        models for UniProt accessions.
    """

    results = await get_list_of_uniprot_summary_helper(list_request)

    if not results:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    return results


@clean_args()
async def get_uniprot_helper(
    qualifier: str,
    provider=None,
    template=None,
    res_range=None,
    uniprot_checksum=None,
):
    f"""Helper function to get uniprot details.

    Args:
        qualifier (str): {UNIPROT_QUAL_DESC}
        provider (str, optional): Data provider
        template (str, optional): {TEMPLATE_DESC}
        res_range (str, optional): Residue range
        uniprot_checksum (str, optional): {UNP_CHECKSUM_DESC}

    Returns:
        Result: A Result object with experimental and theoretical models.
    """
    qualifier = qualifier.upper()
    services = get_services(service_type="uniprot", provider=provider)
    calls = []
    for service in services:
        base_url = get_base_service_url(service["provider"])
        final_url = get_final_service_url(
            base_url, service["accessPoint"], f"{qualifier}.json"
        )

        if res_range:
            final_url = f"{final_url}&range={res_range}"

        calls.append(final_url)

    result = await send_async_requests(calls)
    final_result = [x.json() for x in result if x and x.status_code == 200]

    # filter out beacons results where there are no structures
    final_result = list(filter(lambda x: x.get("structures"), final_result))

    if uniprot_checksum:
        final_result = filter_on_checksum(final_result, uniprot_checksum)

    if not final_result:
        return None

    final_structures: List[Detailed] = []
    uniprot_entry: UniprotEntry = UniprotEntry(
        **get_first_entry_with_checksum(final_result)
    )

    for item in final_result:
        # Remove erroneous responses
        try:
            Detailed(**item["structures"][0])
            UniprotEntry(**item["uniprot_entry"])
            final_structures.extend(item["structures"])
        except pydantic.error_wrappers.ValidationError:
            provider = item["structures"][0].get("provider")
            if provider:
                logger.warning(
                    f"{provider} returned an erroneous response for {qualifier}"
                )
        except Exception:
            pass

    if not final_structures:
        return None

    api_result: UniprotDetails = UniprotDetails(
        **{"uniprot_entry": uniprot_entry, "structures": final_structures}
    )

    return api_result


@uniprot_route.get(
    "/{qualifier}.json",
    status_code=status.HTTP_200_OK,
    response_model=UniprotDetails,
    tags=["UniProt"],
)
async def get_uniprot(
    qualifier: Any = Path(
        ...,
        description="UniProtKB accession number (AC) or entry name (ID)",
        example="P38398",
    ),
    provider: Optional[Any] = Query(
        None, enum=[x["provider"] for x in get_services("uniprot")]
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
    uniprot_checksum: Optional[str] = Query(None, description=UNP_CHECKSUM_DESC),
):
    f"""Returns experimental and theoretical models for a UniProt accession or entry name

    Args:
        qualifier (str): {UNIPROT_QUAL_DESC}
        provider (str, optional): Data provider
        template (str, optional): {TEMPLATE_DESC}
        res_range (str, optional): Residue range
        exclude_provider (str, optional): Provider to exclude
        uniprot_checksum (str, optional): {UNP_CHECKSUM_DESC}

    Returns:
        Result: A Result object with experimental and theoretical models.
    """

    results = await get_uniprot_helper(
        qualifier,
        provider,
        template,
        res_range,
        uniprot_checksum,
    )

    if not results:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)
    else:
        return results
