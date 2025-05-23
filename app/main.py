from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, SessionLocal
from . import models
from .routers import cp, estados, municipios


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Códigos Postales MX",
    description="API para consultar códigos postales de México",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(cp.router)
app.include_router(estados.router)
app.include_router(municipios.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Visita /docs para la documentación de la API"}


@app.on_event("shutdown")
def shutdown_db_connection():
    SessionLocal().close()
