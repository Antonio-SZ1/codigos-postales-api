from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, SessionLocal
from . import models
from .routers import cp, estados, municipios

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Códigos Postales MX",
    description="API para consultar códigos postales de México",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Configurar CORS para Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción usa tu dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(cp.router)
app.include_router(estados.router)
app.include_router(municipios.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Visita /docs para la documentación de la API"}

# Conexión a la base de datos para el contexto
@app.on_event("shutdown")
def shutdown_db_connection():
    SessionLocal().close()
