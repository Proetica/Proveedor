#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def get_results_contrataciones(self, id, filters, page, limit):

        offset = int((page-1) * limit)

        listfilters = [models.Contrataciones.empresa_id == id]

        if filters.monto.data is not None:
            min = float(filters.monto.data.split(" - ")[0])
            max = float(filters.monto.data.split(" - ")[1])
            listfilters.append(
                between(models.Contrataciones.monto, min, max)
            )

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
       
        count = db.query(models.Contrataciones
                        ).filter(
                             and_(*listfilters)
                        ).count()

        pagination = self.get_pager(offset, count, page, limit)

        return [results, pagination]

    def get_max_ammount(self,id, filters):


        listfilters = [models.Contrataciones.empresa_id == id]
       
        if filters.term.data is not None:
            listfilters.append(
                models.Contrataciones.descripcion.ilike('%'+filters.term.data+'%')
            )

        if filters.tipo_moneda.data is not None:
            listfilters.append(
                models.Contrataciones.tipo_moneda.in_(filters.tipo_moneda.data)
            )

        if filters.etiquetas.data is not None:
            listfilters.append(
                or_(
                    models.Contrataciones.etiqueta_fecha.in_(filters.etiquetas.data),
                    models.Contrataciones.etiqueta_monto.in_(filters.etiquetas.data),
                )
            )

        if filters.monto.data is not None:
            min = filters.monto.data.split(" - ")[0]
            max = filters.monto.data.split(" - ")[1]
            listfilters.append(
                between(models.Contrataciones.monto, min, max)
            )


        result = db.query(
            func.max(models.Contrataciones.monto).label("monto")
        ).filter(
            and_(*listfilters)
        ).first()

        return result

    def get_min_ammount(self,id, filters):


        listfilters = [models.Contrataciones.empresa_id == id]
       
        if filters.term.data is not None:
            listfilters.append(
                models.Contrataciones.descripcion.ilike('%'+filters.term.data+'%')
            )

        if filters.tipo_moneda.data is not None:
            listfilters.append(
                models.Contrataciones.tipo_moneda.in_(filters.tipo_moneda.data)
            )

        if filters.etiquetas.data is not None:
            listfilters.append(
                or_(
                    models.Contrataciones.etiqueta_fecha.in_(filters.etiquetas.data),
                    models.Contrataciones.etiqueta_monto.in_(filters.etiquetas.data),
                )
            )

        if filters.monto.data is not None:
            min = filters.monto.data.split(" - ")[0]
            max = filters.monto.data.split(" - ")[1]
            listfilters.append(
                between(models.Contrataciones.monto, min, max)
            )


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