import sys
import os
import csv
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Estado, Municipio, Asentamiento
from app.database import engine

def cargar_datos():
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Limpiar tablas existentes (solo para desarrollo!)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        estados_registrados = set()
        municipios_registrados = set()

        with open('data/codigos_postales.csv', 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f, delimiter='|')
            
            for row in csv_reader:
                # Procesar Estados
                estado_id = row['c_estado'].strip()
                estado_nombre = row['d_estado'].strip().title()
                if (estado_id, estado_nombre) not in estados_registrados:
                    stmt = pg_insert(Estado).values(
                        c_estado=estado_id,
                        nombre=estado_nombre
                    ).on_conflict_do_nothing(index_elements=['c_estado'])
                    db.execute(stmt)
                    estados_registrados.add((estado_id, estado_nombre))
                
                # Procesar Municipios
                municipio_id = row['c_mnpio'].strip()
                municipio_nombre = row['D_mnpio'].strip().title()
                if (municipio_id, estado_id, municipio_nombre) not in municipios_registrados:
                    stmt = pg_insert(Municipio).values(
                        c_mnpio=municipio_id,
                        c_estado=estado_id,
                        nombre=municipio_nombre
                    ).on_conflict_do_nothing(index_elements=['c_mnpio', 'c_estado'])
                    db.execute(stmt)
                    municipios_registrados.add((municipio_id, estado_id, municipio_nombre))
                
                # Procesar Asentamientos
                asentamiento_id = row['id_asenta_cpcons'].zfill(4)
                stmt = pg_insert(Asentamiento).values(
                    id_asenta_cpcons=asentamiento_id,
                    d_codigo=row['d_codigo'].strip(),
                    d_asenta=row['d_asenta'].strip().title(),
                    d_tipo_asenta=row['d_tipo_asenta'].strip(),
                    d_zona=row['d_zona'].strip(),
                    c_mnpio=municipio_id,
                    c_estado=estado_id
                ).on_conflict_do_nothing(index_elements=['id_asenta_cpcons'])
                
                db.execute(stmt)
            
            db.commit()
            print("✅ Datos cargados exitosamente!")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error al cargar datos: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cargar_datos()