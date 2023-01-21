import asyncio
from typing import List

import pydantic
from starlette import status
from starlette.responses import JSONResponse

from app import logger
from app.config import MAX_POST_LIMIT, get_base_service_url, get_services
from app.constants import TEMPLATE_DESC, UNIPROT_QUAL_DESC, UNP_CHECKSUM_DESC
from app.uniprot.schema import (
    AccessionListRequest,
    Overview,
    UniprotEntry,
    UniprotSummary,
)
from app.utils import clean_args, get_final_service_url, send_async_requests


async def get_list_of_uniprot_summary_helper(list_request: AccessionListRequest):
    """Returns summary of experimental and theoretical models for a list of UniProt
    accessions

    Args:
        list_request (AccessionListRequest): List of UniProt accession objects

    Returns:
        Result: A list of Result summary object with experimental and theoretical
        models for UniProt accessions.
    """
    if len(list_request.accessions) > int(MAX_POST_LIMIT):
        return JSONResponse(
            content={
                "message": f"We cannot accept more than {MAX_POST_LIMIT} accessions!"
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    summary_jobs = [
        asyncio.create_task(
            get_uniprot_summary_helper(
                q,
                list_request.provider,
                template=None,
                res_range=None,
                exclude_provider=list_request.exclude_provider,
                uniprot_checksum=None,
            )
        )
        for q in list_request.accessions
    ]

    results = await asyncio.gather(*summary_jobs)

    if not results or all([x is None for x in results]):
        return None

    return [x for x in results if x]


@clean_args()
async def get_uniprot_summary_helper(
    qualifier: str,
    provider=None,
    template=None,
    res_range=None,
    exclude_provider=None,
    uniprot_checksum=None,
):
    f"""Helper function to get uniprot summary.

    Args:
        qualifier (str): {UNIPROT_QUAL_DESC}
        provider (str, optional): Data provider
        template (str, optional): {TEMPLATE_DESC}
        res_range (str, optional): Residue range
        exclude_provider (str, optional): Provider to exclude
        uniprot_checksum (str, optional): {UNP_CHECKSUM_DESC}

    Returns:
        Result: A Result summary object with experimental and theoretical models.
    """
    qualifier = qualifier.upper()
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

    if uniprot_checksum:
        final_result = filter_on_checksum(final_result, uniprot_checksum)

    if not final_result:
        return None

    final_structures: List[Overview] = []
    uniprot_entry: UniprotEntry = UniprotEntry(
        **get_first_entry_with_checksum(final_result)
    )

    for item in final_result:
        # Remove erroneous responses
        try:
            Overview(**item["structures"][0])
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

    api_result: UniprotSummary = UniprotSummary(
        **{"uniprot_entry": uniprot_entry, "structures": final_structures}
    )
    return api_result


def filter_on_checksum(in_result, checksum: str):
    checksum_filtered_list = []

    for item in in_result:
        uniprot_checksum = item["uniprot_entry"].get("uniprot_checksum")
        if uniprot_checksum and uniprot_checksum == checksum:
            checksum_filtered_list.append(item)

    return checksum_filtered_list


def get_first_entry_with_checksum(in_result: List):
    for item in in_result:
        uniprot_checksum = item["uniprot_entry"].get("uniprot_checksum")
        if uniprot_checksum:
            return item["uniprot_entry"]

    if in_result:
        return in_result[0]["uniprot_entry"]

    return None
