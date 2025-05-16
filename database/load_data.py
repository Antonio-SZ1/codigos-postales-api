import sys
import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Añadir el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Estado, Municipio, Asentamiento
from app.database import engine

def cargar_datos():
    # Configurar conexión
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Crear tablas si no existen
        Base.metadata.create_all(engine)

        estados_registrados = set()
        municipios_registrados = set()

        with open('data/codigos_postales.csv', 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f, delimiter='|')
            
            for row in csv_reader:
                # Limpiar y formatear datos
                estado_id = row['c_estado'].strip()
                estado_nombre = row['d_estado'].strip().title()
                municipio_id = row['c_mnpio'].strip()
                municipio_nombre = row['D_mnpio'].strip().title()
                
                # Registrar Estado
                if (estado_id, estado_nombre) not in estados_registrados:
                    estado = Estado(
                        c_estado=estado_id,
                        nombre=estado_nombre
                    )
                    db.add(estado)
                    estados_registrados.add((estado_id, estado_nombre))
                
                # Registrar Municipio
                if (municipio_id, estado_id, municipio_nombre) not in municipios_registrados:
                    municipio = Municipio(
                        c_mnpio=municipio_id,
                        c_estado=estado_id,
                        nombre=municipio_nombre
                    )
                    db.add(municipio)
                    municipios_registrados.add((municipio_id, estado_id, municipio_nombre))
                
                # Registrar Asentamiento
                asentamiento = Asentamiento(
                    id_asenta_cpcons=row['id_asenta_cpcons'].zfill(4),
                    d_codigo=row['d_codigo'].strip(),
                    d_asenta=row['d_asenta'].strip().title(),
                    d_tipo_asenta=row['d_tipo_asenta'].strip(),
                    d_zona=row['d_zona'].strip(),
                    c_mnpio=municipio_id,
                    c_estado=estado_id
                )
                db.add(asentamiento)
            
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