#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Numeric, \
    Unicode, UnicodeText, CHAR, DateTime, ForeignKey, VARCHAR
from sqlalchemy.orm import relationship

Entity = declarative_base()

class TipoGobierno(Entity):
    __tablename__ = 'tipogobierno'

    id = Column(Integer, primary_key=True)
    tipo = Column(UnicodeText, nullable=False)
    entidad = relationship('EntidadGobierno')


class TipoEntidadGobierno(Entity):
    __tablename__ = 'tipoentidadgobierno'

    id = Column(Integer, primary_key=True)
    nombre = Column(UnicodeText, nullable=False)
    entidad = relationship('EntidadGobierno')


class EntidadGobierno(Entity):
    __tablename__ = 'entidadgobierno'

    id = Column(Integer, primary_key=True)
    nombre = Column(UnicodeText, nullable=False)
    tipo_gobierno_id = Column(Integer, ForeignKey('tipogobierno.id'))
    tipo_entidad_id = Column(Integer, ForeignKey('tipoentidadgobierno.id'))
    cargado = Column(Integer, default=0)
    contrato = relationship(
        'Contrataciones',
    )    


class Persona(Entity):
    __tablename__ = 'personas'

    id = Column(Integer, primary_key=True)
    dni = Column(CHAR(20), nullable=False)
    nombre = Column(UnicodeText, nullable=False)
    empresa = relationship(
        'Empresa',
        secondary='empresa_persona'
    )


class Empresa(Entity):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True)
    ruc = Column(Unicode(255), nullable=False)
    razon_social = Column(UnicodeText, nullable=False)
    nombre_comercial = Column(UnicodeText, nullable=True)
    inicio_actividades = Column(DateTime)
    actividades_com_ext = Column(UnicodeText)
    telefono = Column(UnicodeText)
    fax = Column(UnicodeText)
    estado = Column(UnicodeText)
    condicion = Column(UnicodeText)
    direccion = Column(UnicodeText)
    total_ganado = Column(Numeric(15, 2), nullable=True, default=0)
    update = Column(Integer, default=0)
    persona = relationship(
        'Persona',
        secondary='empresa_persona'
    )
    contrato = relationship(
        'Contrataciones',
    )


class Load_empresa(Entity):
    __tablename__ = 'load_empresa'

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer)
    fecha_carga = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now)


class Sucursal(Entity):
    __tablename__ = 'sucursales'

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    tipo = Column(UnicodeText, nullable=False)
    direccion = Column(UnicodeText, nullable=False)


class Empresa_persona(Entity):
    __tablename__ = 'empresa_persona'

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    persona_id = Column(Integer, ForeignKey('personas.id'))
    cargo = Column(UnicodeText, nullable=False)
    fecha_cargo = Column(DateTime)


class Contrataciones(Entity):
    __tablename__ = 'contrataciones'

    id = Column(Integer, primary_key=True)
    fecha_pub = Column(DateTime)
    fecha_bue_pro = Column(DateTime)
    etiqueta_fecha = Column(UnicodeText, nullable=True)
    proceso = Column(UnicodeText, nullable=True)
    objeto_pro = Column(UnicodeText, nullable=True)
    descripcion = Column(UnicodeText, nullable=True)
    valor_ref = Column(Numeric(15, 2), nullable=True, default=0)
    monto = Column(Numeric(15, 2), nullable=True, default=0)
    tipo_moneda = Column(VARCHAR, default='S/.')
    etiqueta_monto = Column(UnicodeText, nullable=True)
    modalidad_sel = Column(UnicodeText, nullable=True)
    detalle_contrato = Column(VARCHAR, nullable=True)
    detalle_seace = Column(VARCHAR, nullable=True, default='ninguna')
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    entidad_id = Column(Integer, ForeignKey('entidadgobierno.id'))

    

if __name__ == '__main__':

    from sqlalchemy import create_engine

    import settings

    db_engine = create_engine(
        settings.DATABASE_DSN,
        echo=settings.DEBUG
    )
    Entity.metadata.create_all(db_engine)
    
    db = sessionmaker(bind=db_engine)()

    _tipo_gobierno = TipoGobierno()
    _tipo_gobierno.id = 3
    _tipo_gobierno.tipo = 'Poder ejecutivo'
    db.add(_tipo_gobierno)

    _tipo_gobierno = TipoGobierno()
    _tipo_gobierno.id = 1
    _tipo_gobierno.tipo = 'Poder legislativo'
    db.add(_tipo_gobierno)

    _tipo_gobierno = TipoGobierno()
    _tipo_gobierno.id = 2
    _tipo_gobierno.tipo = 'Poder judicial'
    db.add(_tipo_gobierno)

    _tipo_gobierno = TipoGobierno()
    _tipo_gobierno.id = 4
    _tipo_gobierno.tipo = 'Organismos autónomos'
    db.add(_tipo_gobierno)

    _tipo_gobierno = TipoGobierno()
    _tipo_gobierno.id = 7
    _tipo_gobierno.tipo = 'Gobiernos regionales'
    db.add(_tipo_gobierno)

    _tipo_gobierno = TipoGobierno()
    _tipo_gobierno.id = 5
    _tipo_gobierno.tipo = 'Gobiernos locales'
    db.add(_tipo_gobierno)

    db.commit()
