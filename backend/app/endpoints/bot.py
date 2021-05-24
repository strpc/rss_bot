from fastapi import APIRouter


router = APIRouter()


@router.post("/message/")
async def new_message():
    return True
