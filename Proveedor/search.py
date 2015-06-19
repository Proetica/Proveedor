#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from math import ceil
import settings
import models
import re
import datetime

db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

db = sessionmaker(bind=db_engine)()


class Search():

    def get_results_contrataciones(self, term, page, limit):

        offset = int((page-1) * limit)

        results = db.query( models.Contrataciones.id,
                            models.Contrataciones.proceso,
                            models.Contrataciones.objeto_pro,
                            models.Contrataciones.fecha_pub,
                            models.Contrataciones.fecha_bue_pro,
                            models.Contrataciones.modalidad_sel,
                            models.Contrataciones.tipo_moneda,
                            models.Contrataciones.monto,
                            models.Contrataciones.valor_ref,
                            models.Contrataciones.descripcion,
                            models.EntidadGobierno.id.label("eid"),
                            models.EntidadGobierno.nombre,
                            models.Contrataciones.empresa_id,
                            models.Empresa.razon_social,
                            models.Empresa.ruc,
                            models.Contrataciones.detalle_contrato,
                            models.Contrataciones.detalle_seace,
                        ).join(
                            models.Empresa,
                            models.EntidadGobierno
                        ).filter(
                            models.Contrataciones.descripcion.ilike('%'+term+'%')
                        ).order_by(
                             models.Empresa.ruc.desc()
                        ).limit(limit).offset(offset)

        count = db.query(models.Contrataciones
                        ).filter(
                            models.Contrataciones.descripcion.ilike('%'+term+'%')
                        ).count()

        pagination = self.get_pager(offset, count, page, limit)

        return [results, pagination]
            

    def get_results_empresas(self, term, page, limit):

        offset = int((page-1) * limit)

        results = db.query(
                                models.Empresa
                            ).filter(
                                or_(
                                    models.Empresa.razon_social.ilike('%' + term + '%'),
                                    models.Empresa.ruc.ilike('%' + term + '%')
                                    )
                            ).limit(limit).offset(offset)

        count = db.query(
                            models.Empresa
                        ).filter(
                            or_(
                                models.Empresa.razon_social.ilike('%' + term + '%'),
                                models.Empresa.ruc.ilike('%' + term + '%')
                                )
                        ).count()

        pagination = self.get_pager(offset, count, page, limit)

        return [results, pagination]


    def get_results_entidades(self, term, page, limit):

        offset = int((page-1) * limit)

        results = db.query(
                        models.EntidadGobierno.id,
                        models.EntidadGobierno.nombre,
                        models.TipoGobierno.tipo
                    ).filter(
                        models.EntidadGobierno.nombre.ilike('%'+term+'%')
                    ).join(
                        models.TipoGobierno
                    ).order_by(
                        models.EntidadGobierno.nombre.desc()
                    ).limit(limit).offset(offset)

        count = db.query(
                        models.EntidadGobierno
                        ).filter(
                            models.EntidadGobierno.nombre.ilike('%'+term+'%')
                        ).count()

        pagination = self.get_pager(offset, count, page, limit)

        return [results, pagination]


    def get_pager(self, index, count, page, limit):

        pagination = {
            'index': index,
            'count': count,
            'pager': int(ceil(count/limit)),
            'page': page,
            'limit': limit
        }

        return pagination