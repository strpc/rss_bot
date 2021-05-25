from fastapi import APIRouter


router = APIRouter()


@router.post("/")
async def new_callback():
    return True
