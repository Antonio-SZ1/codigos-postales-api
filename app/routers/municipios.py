from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Municipio

router = APIRouter(prefix="/api", tags=["Municipios"])

@router.get("/municipios", summary="Obtener municipios por estado")
async def obtener_municipios(estado_id: str = Query(..., min_length=2, max_length=2)):
    db = SessionLocal()
    try:
        municipios = db.query(Municipio).filter(
            Municipio.c_estado == estado_id
        ).all()
        return municipios
    finally:
        db.close()