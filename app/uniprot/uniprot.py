from typing import Any, List, Optional

import pydantic
from fastapi.params import Path, Query
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app import logger
from app.config import get_base_service_url, get_services
from app.constants import TEMPLATE_DESC, UNIPROT_QUAL_DESC
from app.uniprot.schema import (
    Detailed,
    Overview,
    UniprotDetails,
    UniprotEntry,
    UniprotSummary,
)
from app.utils import get_final_service_url, send_async_requests

uniprot_route = APIRouter()


async def get_uniprot_summary_helper(
    qualifier: str, provider=None, template=None, res_range=None, exclude_provider=None
):
    f"""Helper function to get uniprot summary.

    Args:
        qualifier (str): {UNIPROT_QUAL_DESC}
        provider (str, optional): Data provider
        template (str, optional): {TEMPLATE_DESC}
        res_range (str, optional): Residue range
        exclude_provider (str, optional): Provider to exclude

    Returns:
        Result: A Result summary object with experimental and theoretical models.
    """
    qualifier = qualifier.upper().strip(" ")
    if provider:
        provider = provider.strip(" ")
    if template:
        template = template.strip(" ")
    if res_range:
        res_range = res_range.strip(" ")
    if exclude_provider:
        exclude_provider = exclude_provider.strip(" ")

    services = get_services(
        service_type="summary", provider=provider, exclude_provider=exclude_provider
    )
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
    final_result = [
        x.json() for x in result if x and x.status_code == status.HTTP_200_OK
    ]
    if not final_result:
        return None

    final_structures: List[Overview] = []
    uniprot_entry: UniprotEntry = UniprotEntry(**final_result[0]["uniprot_entry"])

    for item in final_result:
        # Remove erroneous responses
        try:
            Overview(**item["structures"][0])
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
        None

    api_result: UniprotSummary = UniprotSummary(
        **{"uniprot_entry": uniprot_entry, "structures": final_structures}
    )
    return api_result


@uniprot_route.get(
    "/summary/{qualifier}.json",
    status_code=status.HTTP_200_OK,
    response_model=UniprotSummary,
    response_model_exclude_unset=True,
)
async def get_uniprot_summary(
    qualifier: Any = Path(..., description=UNIPROT_QUAL_DESC),
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
        None, description="Provider to exclude. eg: pdbe"
    ),
):
    f"""Returns summary of experimental and theoretical models for a UniProt
    accession or entry name

    Args:
        qualifier (str): {UNIPROT_QUAL_DESC}
        provider (str, optional): Data provider
        template (str, optional): {TEMPLATE_DESC}
        res_range (str, optional): Residue range
        exclude_provider (str, optional): Provider to exclude

    Returns:
        Result: A Result summary object with experimental and theoretical models.
    """
    results = await get_uniprot_summary_helper(
        qualifier, provider, template, res_range, exclude_provider
    )

    if not results:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)
    else:
        return results


@uniprot_route.get(
    "/{qualifier}.json", status_code=status.HTTP_200_OK, response_model=UniprotDetails
)
async def get_uniprot(
    qualifier: Any = Path(
        ..., description="UniProtKB accession number (AC) or entry name (ID)"
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
):
    """Returns experimental and theoretical models for a UniProt accession or entry name

    Args:
        qualifier (str): UniProtKB accession number (AC) or entry name (ID).
        provider (str, optional): Data provider
        template (str, optional): 4 letter PDB code, or 4 letter code with assembly ID
        and chain for SMTL entries
        res_range (str, optional): Residue range

    Returns:
        Result: A Result object with experimental and theoretical models.
    """

    qualifier = qualifier.upper().strip(" ")
    if provider:
        provider = provider.strip(" ")
    if template:
        template = template.strip(" ")
    if res_range:
        res_range = res_range.strip(" ")
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

    if not final_result:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    final_structures: List[Detailed] = []
    uniprot_entry: UniprotEntry = UniprotEntry(**final_result[0]["uniprot_entry"])

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
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    api_result: UniprotDetails = UniprotDetails(
        **{"uniprot_entry": uniprot_entry, "structures": final_structures}
    )

    return api_result
