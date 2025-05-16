from pydantic import BaseModel
from typing import List, Optional


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True  


class EstadoBase(BaseSchema):
    c_estado: str
    nombre: str

class EstadoResponse(EstadoBase):
    pass


class MunicipioBase(BaseSchema):
    c_mnpio: str
    nombre: str
    estado_id: str  

class MunicipioResponse(MunicipioBase):
    estado: EstadoResponse


class AsentamientoBase(BaseSchema):
    id_asenta_cpcons: str
    d_codigo: str
    d_asenta: str
    d_tipo_asenta: str
    d_zona: str

class AsentamientoResponse(AsentamientoBase):
    municipio: MunicipioResponse
    estado: EstadoResponse


class ResumenZona(BaseSchema):
    cp: str
    urbano: int
    rural: int


class Message(BaseSchema):
    detail: str