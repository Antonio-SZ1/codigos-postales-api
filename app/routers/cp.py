from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Asentamiento, Municipio, Estado

router = APIRouter(prefix="/api", tags=["Códigos Postales"])

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/codigo", summary="Buscar asentamientos por CP con estado y municipio")
async def buscar_por_cp(cp: str = Query(..., min_length=5, max_length=5, regex="^[0-9]*$"), db: Session = Depends(get_db)):
    resultados = (
        db.query(
            Asentamiento.d_codigo,
            Asentamiento.d_asenta,
            Asentamiento.d_tipo_asenta,
            Asentamiento.d_zona,
            Municipio.nombre.label("municipio"),
            Estado.nombre.label("estado")
        )
        .join(Municipio, (Asentamiento.c_mnpio == Municipio.c_mnpio) & (Asentamiento.c_estado == Municipio.c_estado))
        .join(Estado, Asentamiento.c_estado == Estado.c_estado)
        .filter(Asentamiento.d_codigo == cp)
        .all()
    )

    if not resultados:
        return {"count": 0, "results": []}

    response = []
    for row in resultados:
        response.append({
            "d_codigo": row.d_codigo,
            "d_asenta": row.d_asenta,
            "d_tipo_asenta": row.d_tipo_asenta,
            "d_zona": row.d_zona,
            "municipio": row.municipio,
            "estado": row.estado
        })

    return {"count": len(response), "results": response}

@router.get("/resumen-zona", summary="Resumen por zona de un CP")
async def resumen_zona(cp: str = Query(..., min_length=5, max_length=5), db: Session = Depends(get_db)):
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
