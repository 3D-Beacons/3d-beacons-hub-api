from typing import Any, Dict, List, Optional, Set

from fastapi.params import Path, Query
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.config import GIFTS_API, MAX_POST_LIMIT, get_services
from app.constants import ENSEMBL_QUAL_DESC
from app.ensembl.schema import EnsemblSummary
from app.uniprot.helper import (
    get_list_of_uniprot_summary_helper,
    get_uniprot_api_results,
    get_uniprot_name,
)
from app.uniprot.schema import AccessionListRequest
from app.utils import clean_args, request_get

ensembl_route = APIRouter()


@ensembl_route.get(
    "/summary/{qualifier}.json",
    status_code=status.HTTP_200_OK,
    response_model=EnsemblSummary,
    response_model_exclude_unset=True,
    tags=["Ensembl"],
)
async def get_ensembl_summary(
    qualifier: Any = Path(
        ..., description=ENSEMBL_QUAL_DESC, example="ENSG00000288864"
    ),
    provider: Optional[Any] = Query(
        None, enum=[x["provider"] for x in get_services("summary")]
    ),
):
    f"""Returns summary of experimental and theoretical models for an Ensembl gene ID.

    Args:
        qualifier (str): {ENSEMBL_QUAL_DESC}
        provider (str, optional): Data provider

    Returns:
        Result: A Result summary object with experimental and theoretical models.
    """
    ensembl_summary = await get_ensembl_summary_helper(qualifier, provider)

    if not ensembl_summary:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    return ensembl_summary


@clean_args()
async def get_ensembl_summary_helper(
    qualifier: str,
    provider=None,
):
    f"""Returns summary of experimental and theoretical models for a UniProt
    accession or entry name

    Args:
        qualifier (str): {ENSEMBL_QUAL_DESC}
        provider (str, optional): Data provider

    Returns:
        Result: A Result summary object with experimental and theoretical models.
    """
    qualifier = qualifier.upper()

    ensembl_mappings = await get_ensembl_mappings(qualifier)

    if not ensembl_mappings:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    transcript_dict: Dict[str, List] = {}
    uniprot_request_list = AccessionListRequest(accessions=[], provider=provider)
    uniprot_set: Set = set()

    for mapping in ensembl_mappings["entryMappings"]:
        if len(uniprot_set) >= MAX_POST_LIMIT:
            break

        uniprot_accession = mapping["uniprotEntry"]["uniprotAccession"]
        uniprot_set.add(uniprot_accession)

        mapping["ensemblTranscript"].update(
            {"alignment_difference": mapping["alignment_difference"]}
        )

        if not transcript_dict.get(uniprot_accession):
            transcript_dict[uniprot_accession] = []

        transcript_dict[uniprot_accession].append(mapping["ensemblTranscript"])

    uniprot_request_list.accessions = list(uniprot_set)
    uniprot_summary = await get_list_of_uniprot_summary_helper(uniprot_request_list)
    uniprot_api_response = await get_uniprot_api_results(
        uniprot_request_list.accessions
    )

    if not uniprot_summary:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    results = {
        "ensembl_id": qualifier,
        "species": ensembl_mappings["taxonomy"]["species"],
        "taxid": ensembl_mappings["taxonomy"]["ensemblTaxId"],
        "uniprot_mappings": [],
    }

    for uniprot in uniprot_summary:
        uniprot_response = uniprot_api_response.get(uniprot.uniprot_entry.ac)
        uniprot.uniprot_entry.description = get_uniprot_name(uniprot_response)

        for ensembl_transcript in transcript_dict[uniprot.uniprot_entry.ac]:
            results["uniprot_mappings"].append(
                {
                    "ensembl_transcript": ensembl_transcript,
                    "uniprot_accession": uniprot,
                }
            )

    return results


async def get_ensembl_mappings(qualifier: str):
    f"""Get UniProt mappings for a gene ID.

    Args:
        qualifier (str): {ENSEMBL_QUAL_DESC}

    Returns:
        Dict: Mappings for a gene ID.
    """
    result = await request_get(f"{GIFTS_API}?searchTerm={qualifier}&format=json")

    if result.status_code == status.HTTP_200_OK:
        return result.json().get("results")[0]

    return None
