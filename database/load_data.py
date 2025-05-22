#!/usr/bin/env python3
import os
import csv
import sys
import argparse
import logging

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

# Solo cargar dotenv si no estamos en Render
if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# Path para imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Estado, Municipio, Asentamiento

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def crear_tablas(engine, reset: bool):
    """Crear (y opcionalmente resetear) esquema."""
    if reset:
        logger.warning("⚠️ DEBUG: Eliminando todas las tablas...")
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logger.info("🧱 Tablas listas.")


def chunked(iterable, size):
    """Divide la lista en trozos de tamaño `size`."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def parse_args():
    p = argparse.ArgumentParser(description="Carga masiva de códigos postales")
    p.add_argument(
        "--csv",
        type=str,
        default="data/codigos_postales.csv",
        help="Ruta al archivo CSV de entrada"
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Número de filas por lote para upsert"
    )
    return p.parse_args()


def cargar_datos(csv_path: str, batch_size: int):
    DATABASE_URL   = os.getenv("DATABASE_URL")
    DEBUG_RESET_DB = os.getenv("DEBUG_RESET_DB", "false").lower() == "true"

    if not DATABASE_URL:
        logger.critical("❌ La variable de entorno DATABASE_URL no está definida.")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

    # Prepara esquema
    crear_tablas(engine, DEBUG_RESET_DB)

    # Lee todo en memoria para contar y validar columnas
    with open(csv_path, newline='', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="|")
        rows = list(reader)

    total = len(rows)
    if total == 0:
        logger.warning("⚠️ El CSV está vacío: %s", csv_path)
        return

    # Verificar columnas mínimas
    sample = rows[0]
    required = {"c_estado", "d_estado", "c_mnpio", "D_mnpio", "d_codigo", "id_asenta_cpcons", "d_asenta", "d_tipo_asenta", "d_zona"}
    missing = required - set(sample.keys())
    if missing:
        logger.error("❌ Faltan columnas en el CSV: %s", missing)
        sys.exit(1)

    estados_cache    = set()
    municipios_cache = set()
    asentamientos    = []

    # Procesamiento en memoria
    from tqdm import tqdm
    for row in tqdm(rows, desc="Parseando filas", unit="reg"):
        estado_id       = row['c_estado'].strip().zfill(2)
        estado_nombre   = row['d_estado'].strip().title()

        municipio_id    = row['c_mnpio'].strip().zfill(3)
        municipio_nombre= row['D_mnpio'].strip().title()

        cp              = row['d_codigo'].strip().zfill(5)

        asentamiento_id = row['id_asenta_cpcons'].strip().zfill(4)
        d_asenta        = row['d_asenta'].strip().title()
        d_tipo          = row['d_tipo_asenta'].strip()
        zona            = row['d_zona'].strip().title()
        zona            = zona if zona in ("Urbano","Rural") else "Urbano"

        estados_cache.add((estado_id, estado_nombre))
        municipios_cache.add((estado_id, municipio_id, municipio_nombre))

        asentamientos.append({
            "id_asenta_cpcons": asentamiento_id,
            "d_codigo": cp,
            "d_asenta": d_asenta,
            "d_tipo_asenta": d_tipo,
            "d_zona": zona,
            "c_mnpio": municipio_id,
            "c_estado": estado_id,
        })

    logger.info("✓ Filas parseadas: %d", total)
    logger.info("✓ Estados distintos a insertar: %d", len(estados_cache))
    logger.info("✓ Municipios distintos a insertar: %d", len(municipios_cache))
    logger.info("✓ Asentamientos totales a procesar: %d", len(asentamientos))

    # Inserción en la base de datos
    with engine.begin() as conn:  # abre transacción
        # Upsert de estados
        for est_id, est_nom in estados_cache:
            stmt = insert(Estado).values(c_estado=est_id, nombre=est_nom)
            stmt = stmt.on_conflict_do_nothing(index_elements=["c_estado"])
            conn.execute(stmt)

        # Upsert de municipios
        for est_id, mun_id, mun_nom in municipios_cache:
            stmt = insert(Municipio).values(
                c_estado=est_id,
                c_mnpio=mun_id,
                nombre=mun_nom
            )
            stmt = stmt.on_conflict_do_nothing(index_elements=["c_estado","c_mnpio"])
            conn.execute(stmt)

        # Upsert de asentamientos por lotes
        for batch in chunked(asentamientos, batch_size):
            stmt = insert(Asentamiento).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id_asenta_cpcons"])
            conn.execute(stmt)

    logger.info("✅ Carga completada sin errores.")

if __name__ == "__main__":
    args = parse_args()
    cargar_datos(args.csv, args.batch_size)
