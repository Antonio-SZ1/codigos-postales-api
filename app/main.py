from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import cp, estados, municipios
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Códigos Postales MX",
    description="API para consultar códigos postales de México",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(cp.router)
app.include_router(estados.router)
app.include_router(municipios.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Visita /docs para la documentación de la API"}