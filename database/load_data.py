import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Estado, Municipio, Asentamiento

def cargar_datos():
    engine = create_engine("postgresql://cp_user:secret123@db:5432/codigos_postales")
    Session = sessionmaker(bind=engine)
    db = Session()

    estados_registrados = set()
    municipios_registrados = set()

    with open('data/codigos_postales.csv', 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, delimiter='|')
        
        for row in csv_reader:
            # Registrar Estado
            estado_key = (row['c_estado'], row['d_estado'].strip().title())
            if estado_key not in estados_registrados:
                estado = Estado(
                    c_estado=row['c_estado'],
                    nombre=estado_key[1]
                )
                db.add(estado)
                estados_registrados.add(estado_key)
            
            # Registrar Municipio
            municipio_key = (row['c_mnpio'], row['c_estado'], row['D_mnpio'].strip().title())
            if municipio_key not in municipios_registrados:
                municipio = Municipio(
                    c_mnpio=row['c_mnpio'],
                    c_estado=row['c_estado'],
                    nombre=municipio_key[2]
                )
                db.add(municipio)
                municipios_registrados.add(municipio_key)
            
            # Registrar Asentamiento
            asentamiento = Asentamiento(
                id_asenta_cpcons=row['id_asenta_cpcons'].zfill(4),
                d_codigo=row['d_codigo'],
                d_asenta=row['d_asenta'].strip().title(),
                d_tipo_asenta=row['d_tipo_asenta'].strip(),
                d_zona=row['d_zona'].strip(),
                c_mnpio=row['c_mnpio'],
                c_estado=row['c_estado']
            )
            db.add(asentamiento)
        
        db.commit()
        db.close()

if __name__ == "__main__":
    cargar_datos()