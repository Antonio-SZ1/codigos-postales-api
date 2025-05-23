import os
import csv
import sys
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker


if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Estado, Municipio, Asentamiento

DATABASE_URL   = os.getenv("DATABASE_URL")
DEBUG_RESET_DB = os.getenv("DEBUG_RESET_DB", "false").lower() == "true"

def crear_tablas(engine):
    if DEBUG_RESET_DB:
        print("⚠️ DEBUG: Eliminando todas las tablas...")
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("🧱 Tablas listas.")

def chunked(iterable, size):
    """Divide una lista en trozos de tamaño `size`."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]

def safe_val(row, key, zfill=None, title=False):
    """
    Devuelve row[key].strip() (o '' si es None), opcionalmente zfilled 
    y/o titulado.
    """
    v = row.get(key)
    if v is None:
        s = ''
    else:
        s = v.strip()
    if title:
        s = s.title()
    if zfill and s.isdigit():
        s = s.zfill(zfill)
    return s

def cargar_datos():
    if not DATABASE_URL:
        raise RuntimeError("❌ La variable DATABASE_URL no está definida.")

    engine  = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db       = Session()

    try:
        crear_tablas(engine)

        estados_cache        = set()
        municipios_cache     = set()
        asentamientos_buffer = []

        registros_procesados = 0
        errores              = 0

        with open('data/codigos_postales.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter='|')
            total  = sum(1 for _ in reader)
            f.seek(0)
            reader = csv.DictReader(f, delimiter='|')

            print(f"\n📊 Iniciando carga de {total} registros...\n")

            for idx, row in enumerate(reader, 1):
                try:
               
                    estado_id        = safe_val(row, 'c_estado', zfill=2)
                    estado_nombre    = safe_val(row, 'd_estado', title=True)
                    municipio_id     = safe_val(row, 'c_mnpio', zfill=3)
                    municipio_nombre = safe_val(row, 'd_mnpio', title=True)
                    cp               = safe_val(row, 'd_codigo', zfill=5)
                    zona             = safe_val(row, 'd_zona', title=True)
                    zona             = zona if zona in ['Urbano', 'Rural'] else 'Urbano'
                    asenta_id        = safe_val(row, 'id_asenta_cpcons', zfill=4)

                  
                    if not cp or not asenta_id:
                        raise ValueError(f"Falta campo crítico en línea {idx}")

                
                    key_est = (estado_id, estado_nombre)
                    if key_est not in estados_cache:
                        stmt = insert(Estado).values(
                            c_estado=estado_id,
                            nombre=estado_nombre
                        ).on_conflict_do_nothing()
                        db.execute(stmt)
                        estados_cache.add(key_est)

                 
                    key_mun = (estado_id, municipio_id, municipio_nombre)
                    if key_mun not in municipios_cache:
                        stmt = insert(Municipio).values(
                            c_mnpio=municipio_id,
                            c_estado=estado_id,
                            nombre=municipio_nombre
                        ).on_conflict_do_nothing()
                        db.execute(stmt)
                        municipios_cache.add(key_mun)

              
                    asentamientos_buffer.append({
                        "id_asenta_cpcons": asenta_id,
                        "d_codigo":         cp,
                        "d_asenta":         safe_val(row, 'd_asenta', title=True),
                        "d_tipo_asenta":    safe_val(row, 'd_tipo_asenta'),
                        "d_zona":           zona,
                        "c_mnpio":          municipio_id,
                        "c_estado":         estado_id
                    })

                    registros_procesados += 1
                    if idx % 1000 == 0:
                        print(f"⏳ Procesados {idx}/{total}…")

                except Exception as e:
                    errores += 1
                    print(f"❌ Error en línea {idx}: {e}")
                    db.rollback()
                    continue

      
        for batch in chunked(asentamientos_buffer, 1000):
            stmt = insert(Asentamiento).values(batch)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['id_asenta_cpcons', 'd_codigo']
            )
            db.execute(stmt)
        db.commit()

        print(f"""
✅ Carga completada.
----------------------------
Total registros leídos  : {total}
Registros procesados    : {registros_procesados}
Estados insertados      : {len(estados_cache)}
Municipios insertados   : {len(municipios_cache)}
Errores                 : {errores}
""")

    except Exception as e:
        db.rollback()
        print(f"🔥 Error fatal: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cargar_datos()
