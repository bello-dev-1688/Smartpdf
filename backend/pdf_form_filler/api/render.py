from fastapi import APIRouter
from fastapi.responses import Response

from pdf_form_filler.api.dependencies import service
from pdf_form_filler.api.errors import to_http


router = APIRouter(prefix="/documents/{document_id}")


@router.get("/pages/{page_number}/render")
def render(
    document_id: str,
    page_number: int,
    zoom: float = 1.0,
):
    try:
        return Response(
            service.render_page(
                document_id,
                page_number,
                zoom,
            ),
            media_type="image/png",
        )
    except Exception as error:
        raise to_http(error)