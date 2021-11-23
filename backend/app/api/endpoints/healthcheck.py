from fastapi import APIRouter, status
from starlette.responses import Response


router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck() -> Response:
    return Response(status_code=status.HTTP_200_OK)
