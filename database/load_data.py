import os
import csv
from sqlalchemy import create_engine, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from app.models import Base, Estado, Municipio, Asentamiento

def cargar_datos():
    # Configurar conexión
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        print("🔄 Iniciando carga de datos...")
        
        # Diccionarios para evitar duplicados
        estados_cache = set()
        municipios_cache = set()

        with open('data/codigos_postales.csv', 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.DictReader(f, delimiter='|')
            total = sum(1 for _ in csv_reader)  # Contar total de registros
            f.seek(0)
            csv_reader = csv.DictReader(f, delimiter='|')

            print(f"📦 Total de registros a procesar: {total}")

            for idx, row in enumerate(csv_reader, 1):
                # Normalizar datos
                estado_id = row['c_estado'].strip().zfill(2)
                estado_nombre = row['d_estado'].strip().title()
                municipio_id = row['c_mnpio'].strip().zfill(3)
                municipio_nombre = row['D_mnpio'].strip().title()
                cp = row['d_codigo'].strip().zfill(5)

                # Insertar Estado si no existe
                if (estado_id, estado_nombre) not in estados_cache:
                    stmt = pg_insert(Estado).values(
                        c_estado=estado_id,
                        nombre=estado_nombre
                    ).on_conflict_do_nothing(index_elements=['c_estado'])
                    db.execute(stmt)
                    estados_cache.add((estado_id, estado_nombre))

                # Insertar Municipio si no existe
                municipio_key = (estado_id, municipio_id, municipio_nombre)
                if municipio_key not in municipios_cache:
                    stmt = pg_insert(Municipio).values(
                        c_mnpio=municipio_id,
                        c_estado=estado_id,
                        nombre=municipio_nombre
                    ).on_conflict_do_nothing(index_elements=['c_mnpio', 'c_estado'])
                    db.execute(stmt)
                    municipios_cache.add(municipio_key)

                # Insertar Asentamiento
                stmt = pg_insert(Asentamiento).values(
                    id_asenta_cpcons=row['id_asenta_cpcons'].strip().zfill(4),
                    d_codigo=cp,
                    d_asenta=row['d_asenta'].strip().title(),
                    d_tipo_asenta=row['d_tipo_asenta'].strip(),
                    d_zona=row['d_zona'].strip(),
                    c_mnpio=municipio_id,
                    c_estado=estado_id
                ).on_conflict_do_nothing(index_elements=['id_asenta_cpcons'])

                db.execute(stmt)

                # Commit cada 500 registros
                if idx % 500 == 0:
                    db.commit()
                    print(f"⏳ Progreso: {idx}/{total} ({idx/total:.1%})")

            db.commit()
            print(f"""
            ✅ Carga completada con éxito!
            - Estados insertados: {len(estados_cache)}
            - Municipios insertados: {len(municipios_cache)}
            - Asentamientos insertados: {total}
            """)

    except Exception as e:
        db.rollback()
        print(f"❌ Error crítico: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cargar_datos()
