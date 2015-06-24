#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request
from sqlalchemy import create_engine, and_, or_, func, between
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


class AdvanceSearch():

    def generateFilters(self, filters, id):

        listfilters = []

        listfilters.append(models.Contrataciones.empresa_id == id)

        if filters.monto.data:
            min = float(filters['monto'].data.split(" - ")[0])
            max = float(filters['monto'].data.split(" - ")[1])
            listfilters.append(
                and_(
                    between(models.Contrataciones.monto, min, max)
                )
            )

        if filters.etiquetas.data:
            listfilters.append(
                and_(
                    or_(
                        models.Contrataciones.etiqueta_fecha.in_(filters.etiquetas.data),
                        models.Contrataciones.etiqueta_monto.in_(filters.etiquetas.data)
                    )
                )
            )
     
        if filters.term.data:
            listfilters.append(
                and_(
                    models.Contrataciones.descripcion.ilike('%'+filters.term.data+'%')
                )
            )

        if filters.tipo_moneda.data:
            listfilters.append(
                and_(
                    models.Contrataciones.tipo_moneda.in_(filters.tipo_moneda.data)
                )
            )

        if filters.fecha_inicial.data:
            inicio = filters.fecha_inicial.data
            final = filters.fecha_final.data
            listfilters.append(
                and_(inicio >  models.Contrataciones.fecha_bue_pro < final)
            )

        return listfilters


    def get_results_contrataciones(self, id, filters, page, limit):

        offset = int((page-1) * limit)

        listfilters = self.generateFilters(filters, id)

        results = db.query(
            models.Contrataciones.id,
            models.Contrataciones.proceso,
            models.Contrataciones.objeto_pro,
            models.Contrataciones.fecha_pub,
            models.Contrataciones.fecha_bue_pro,
            models.Contrataciones.etiqueta_fecha,
            models.Contrataciones.modalidad_sel,
            models.Contrataciones.tipo_moneda,
            models.Contrataciones.monto,
            models.Contrataciones.valor_ref,
            models.Contrataciones.etiqueta_monto,
            models.Contrataciones.descripcion,
            models.Contrataciones.entidad_id,
            models.EntidadGobierno.nombre,
            models.Contrataciones.detalle_contrato,
            models.Contrataciones.detalle_seace,
            models.Contrataciones.empresa_id,
            models.Empresa.id.label("idempresa"),
            models.Empresa.razon_social
        ).join(
            models.EntidadGobierno,
            models.Empresa
        ).filter(
                 and_(*listfilters)
        ).order_by(
             models.Contrataciones.fecha_bue_pro.desc(),
             models.Contrataciones.monto.desc()
        ).limit(limit).offset(offset)
       
        count = results.count()

        pagination = self.get_pager(offset, count, page, limit)

        return [results, pagination]

    def get_max_ammount(self,id, filters):

        listfilters = self.generateFilters(filters, id)

        result = db.query(
            func.max(models.Contrataciones.monto).label("monto")
        ).filter(
            and_(*listfilters)
        ).first()

        return result

    def get_min_ammount(self,id, filters):

        listfilters = self.generateFilters(filters, id)

        result = db.query(
            func.min(models.Contrataciones.monto).label("monto")
        ).filter(
            and_(*listfilters)
        ).first()

        return result

    def get_pager(self, index, count, page, limit):

        pagination = {
            'index': index,
            'count': count,
            'pager': int(ceil(count/limit)),
            'page': page,
            'limit': limit
        }

        return pagination