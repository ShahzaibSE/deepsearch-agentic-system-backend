from fastapi import APIRouter, Request

router = APIRouter()

@router.get('/test')
async def test(req: Request):
    return 'Tested Successfully'