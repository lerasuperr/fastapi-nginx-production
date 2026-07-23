from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("")
async def get_users():
    return [
        {
            "id": 1,
            "name": "Alice"
        },
        {
            "id": 2,
            "name": "Valeria"
        }
    ]