from fastapi import APIRouter, Response


router = APIRouter()


@router.post("/")
async def new_callback() -> Response:
    return Response(status_code=200)
