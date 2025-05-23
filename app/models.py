from sqlalchemy import Column, String, ForeignKey, ForeignKeyConstraint, Index
from .database import Base

class Estado(Base):
    __tablename__ = "estados"
    c_estado = Column(String(2), primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)

class Municipio(Base):
    __tablename__ = "municipios"
    c_mnpio = Column(String(3), primary_key=True)
    c_estado = Column(String(2), ForeignKey('estados.c_estado'), primary_key=True)
    nombre = Column(String(100), nullable=False)

class Asentamiento(Base):
    __tablename__ = "asentamientos"
    id_asenta_cpcons = Column(String(4), primary_key=True)
    d_codigo = Column(String(5), nullable=False)
    d_asenta = Column(String(150), nullable=False)
    d_tipo_asenta = Column(String(50), nullable=False)
    d_zona = Column(String(10), nullable=False)
    c_mnpio = Column(String(3), nullable=False)
    c_estado = Column(String(2), nullable=False)
    
    __table_args__ = (
        ForeignKeyConstraint(
            ['c_mnpio', 'c_estado'],
            ['municipios.c_mnpio', 'municipios.c_estado']
        ),
        Index('idx_asenta_unique', 'id_asenta_cpcons', 'd_codigo', unique=True)
    )
