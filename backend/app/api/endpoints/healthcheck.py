from fastapi import APIRouter, status
from starlette.responses import JSONResponse


router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck() -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK)
