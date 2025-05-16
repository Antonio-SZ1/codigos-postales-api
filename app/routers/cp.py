from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Asentamiento

router = APIRouter(prefix="/api", tags=["Códigos Postales"])

@router.get("/codigo", summary="Buscar asentamientos por CP")
async def buscar_por_cp(cp: str = Query(..., min_length=5, max_length=5, regex="^[0-9]*$")):
    db = SessionLocal()
    try:
        resultados = db.query(Asentamiento).filter(Asentamiento.d_codigo == cp).all()
        return {"count": len(resultados), "results": resultados}
    finally:
        db.close()

@router.get("/resumen-zona", summary="Resumen por zona de un CP")
async def resumen_zona(cp: str = Query(..., min_length=5, max_length=5)):
    db = SessionLocal()
    try:
        urbano = db.query(Asentamiento).filter(
            Asentamiento.d_codigo == cp,
            Asentamiento.d_zona == "Urbano"
        ).count()
        
        rural = db.query(Asentamiento).filter(
            Asentamiento.d_codigo == cp,
            Asentamiento.d_zona == "Rural"
        ).count()
        
        return {
            "cp": cp,
            "urbano": urbano,
            "rural": rural
        }
    finally:
        db.close()