from typing import Any, Optional

from fastapi import Path, Query
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from starlette import status

from app.annotations.schema import Annotation, FeatureType
from app.config import get_base_service_url, get_services
from app.constants import UNIPROT_ID_PARAM, UNIPROT_QUAL_DESC, UNIPROT_RANGE_DESC
from app.utils import clean_args, get_final_service_url, send_async_requests

annotations_route = APIRouter()


@annotations_route.get(
    "/{uniprot_qualifier}.json",
    status_code=status.HTTP_200_OK,
    summary="Get annotations for a UniProt residue range",
    description="Get annotations for a range of UniProt residues.",
    response_model=Annotation,
    tags=["Annotations"],
    response_model_exclude_unset=True,
    include_in_schema=True,
    response_model_exclude_none=True,
)
async def get_annotations_api(
    uniprot_qualifier: Any = Path(
        ..., description=UNIPROT_QUAL_DESC, example=UNIPROT_ID_PARAM
    ),
    annotation_type: FeatureType = Query(
        ..., description="Annotation type", alias="type"
    ),
    provider: Optional[Any] = Query(
        None, enum=[x["provider"] for x in get_services("annotations")]
    ),
    res_range: Any = Query(None, alias="range", description=UNIPROT_RANGE_DESC),
):
    f"""Returns annotation details for a UniProt accession

    Args:
        uniprot_qualifier (Any): {UNIPROT_QUAL_DESC}
        range (Any, optional): {UNIPROT_RANGE_DESC} Defaults to None.
        provider (str, optional): Data provider
        annotation_type (FeatureType, optional): Annotation type.

    Raises:
        HTTPException: Raised when there are validation issues with parameters

    Returns:
        Result: A Annotations model
    """

    uniprot_qualifier = uniprot_qualifier.upper()

    results = await get_annotations_api_helper(
        uniprot_qualifier, annotation_type, provider, res_range
    )

    if not results:
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)

    return results


@clean_args()
async def get_annotations_api_helper(
    uniprot_qualifier: str,
    annotation_type: str,
    provider: Optional[str] = None,
    res_range: Optional[str] = None,
):
    """Helper function for get_annotations_api"""
    qualifier = uniprot_qualifier.upper()
    services = get_services(
        service_type="annotations",
        provider=provider,
    )
    calls = []
    for service in services:
        base_url = get_base_service_url(service["provider"])
        final_url = get_final_service_url(
            base_url, service["accessPoint"], f"{qualifier}.json"
        )
        final_url = f"{final_url}&type={annotation_type}"
        if res_range:
            final_url = f"{final_url}&range={res_range}"

        calls.append(final_url)

    result = await send_async_requests(calls)
    final_result = [
        x.json() for x in result if x and x.status_code == status.HTTP_200_OK
    ]

    if not final_result:
        return None

    annotations = []

    for result in final_result:
        annotations.extend(result["annotation"])

    return Annotation(
        accession=uniprot_qualifier,
        id=final_result[0]["id"],
        sequence=final_result[0]["sequence"],
        annotation=annotations,
    )
