import os
import csv
import sys
from sqlalchemy import create_engine, exc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from dotenv import load_dotenv

# Configurar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Estado, Municipio, Asentamiento

def cargar_datos():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Limpiar tablas existentes (solo para desarrollo)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        estados_cache = set()
        municipios_cache = set()
        registros_procesados = 0
        errores = 0

        with open('data/codigos_postales.csv', 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.DictReader(f, delimiter='|')
            total = sum(1 for _ in csv_reader)
            f.seek(0)
            csv_reader = csv.DictReader(f, delimiter='|')

            print(f"\n📊 Iniciando carga de {total} registros...")

            for idx, row in enumerate(csv_reader, 1):
                try:
                    # Normalizar campos
                    estado_id = row['c_estado'].strip().zfill(2)
                    estado_nombre = row['d_estado'].strip().title()
                    municipio_id = row['c_mnpio'].strip().zfill(3)
                    municipio_nombre = row['D_mnpio'].strip().title()
                    cp = row['d_codigo'].strip().zfill(5)
                    
                    # Sanitizar campo d_zona
                    d_zona = row['d_zona'].strip().title()
                    if d_zona not in ['Urbano', 'Rural']:
                        d_zona = 'Urbano'  # Valor por defecto para datos inconsistentes

                    # Insertar Estado
                    estado_key = (estado_id, estado_nombre)
                    if estado_key not in estados_cache:
                        stmt = insert(Estado).values(
                            c_estado=estado_id,
                            nombre=estado_nombre
                        ).on_conflict_do_nothing()
                        db.execute(stmt)
                        estados_cache.add(estado_key)

                    # Insertar Municipio
                    municipio_key = (estado_id, municipio_id, municipio_nombre)
                    if municipio_key not in municipios_cache:
                        stmt = insert(Municipio).values(
                            c_mnpio=municipio_id,
                            c_estado=estado_id,
                            nombre=municipio_nombre
                        ).on_conflict_do_nothing()
                        db.execute(stmt)
                        municipios_cache.add(municipio_key)

                    # Insertar Asentamiento
                    stmt = insert(Asentamiento).values(
                        id_asenta_cpcons=row['id_asenta_cpcons'].strip().zfill(4),
                        d_codigo=cp,
                        d_asenta=row['d_asenta'].strip().title(),
                        d_tipo_asenta=row['d_tipo_asenta'].strip(),
                        d_zona=d_zona,
                        c_mnpio=municipio_id,
                        c_estado=estado_id
                    ).on_conflict_do_nothing()

                    db.execute(stmt)
                    registros_procesados += 1

                    # Commit parcial cada 500 registros
                    if idx % 500 == 0:
                        db.commit()
                        print(f"⏳ Progreso: {idx}/{total} ({idx/total:.1%}) | Errores: {errores}")

                except exc.IntegrityError as e:
                    db.rollback()
                    errores += 1
                    print(f"❌ Error en registro {idx}: {str(e)}")
                    continue

                except Exception as e:
                    db.rollback()
                    errores += 1
                    print(f"❌ Error crítico en registro {idx}: {str(e)}")
                    continue

            db.commit()
            print(f"""
            ✅ Carga completada!
            - Registros procesados: {registros_procesados}
            - Errores: {errores}
            - Estados: {len(estados_cache)}
            - Municipios: {len(municipios_cache)}
            """)

    except Exception as e:
        db.rollback()
        print(f"🔥 Error fatal: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cargar_datos()