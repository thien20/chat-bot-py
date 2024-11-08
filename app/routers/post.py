from fastapi import Depends, Response, status, HTTPException, APIRouter

router = APIRouter(
    prefix="/",
    tags=["post"],
)