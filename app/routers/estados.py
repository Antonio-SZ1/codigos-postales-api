from fastapi import APIRouter
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Estado

router = APIRouter(prefix="/api", tags=["Estados"])

@router.get("/estados", summary="Obtener todos los estados")
async def obtener_estados():
    db = SessionLocal()
    try:
        estados = db.query(Estado).all()
        return estados
    finally:
        db.close()