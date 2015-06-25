#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, g, render_template, url_for, request, redirect
from sqlalchemy import create_engine, or_, and_, func, extract, desc, asc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from search_form import SearchFormProveedor
from search_form import SearchTerm
from search_form import SearchFormEntidad
import models, settings
import search, advance_search
import json

app = Flask(
    __name__,
    static_folder=settings.STATIC_PATH,
    static_url_path=settings.STATIC_URL_PATH
)

app.config.from_object('settings')

db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

@app.before_request
def before_request():
    g.db = sessionmaker(
        bind=db_engine
    )()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def index():


    top = {'2015':'','2014':'','2013':'',
            '2012':'','2011':'','2010':'','2009':''}
    top[2015] = topEmpresas(2015)
    top[2014] = topEmpresas(2014)
    top[2013] = topEmpresas(2013)
    top[2012] = topEmpresas(2012)
    top[2011] = topEmpresas(2011)
    top[2010] = topEmpresas(2010)
    top[2009] = topEmpresas(2009)

    topentidades = {'2015':'','2014':'','2013':'',
            '2012':'','2011':'','2010':'','2009':''}

    topentidades[2015] = topEntidades(2015)
    topentidades[2014] = topEntidades(2014)
    topentidades[2013] = topEntidades(2013)
    topentidades[2012] = topEntidades(2012)
    topentidades[2011] = topEntidades(2011)
    topentidades[2010] = topEntidades(2010)
    topentidades[2009] = topEntidades(2009)

    contratos = g.db.query(models.Contrataciones).count()

    empresas = g.db.query(models.Empresa).count()

    entidades = g.db.query(models.EntidadGobierno).count()

    cont_irre = g.db.query(
                models.Contrataciones
            ).filter(
                or_(models.Contrataciones.etiqueta_fecha == 'irregulares',
                    models.Contrataciones.etiqueta_fecha == 'cercanas')
            ).count()

    total = g.db.query(
                extract('year', models.Contrataciones.fecha_bue_pro).label("anio"),
                func.sum(models.Contrataciones.monto).label("total")
            ).filter(
                    models.Contrataciones.tipo_moneda == 'S/.'
            ).group_by('anio').order_by('anio').all()


    total = g.db.query(
                extract('year', models.Contrataciones.fecha_bue_pro).label("anio"),
                func.sum(models.Contrataciones.monto).label("total")
            ).filter(
                    models.Contrataciones.tipo_moneda == 'S/.'
            ).group_by('anio').order_by('anio').all()

    proveedores = g.db.query(
                extract('year', models.Contrataciones.fecha_bue_pro).label("anio"),
                func.count(models.Contrataciones.id).label("cantidad")
            ).order_by(asc('anio')).group_by('anio').all()

    total_soles = g.db.query(
                func.sum(models.Contrataciones.monto).label("total")
            ).filter(
                and_(
                    extract('year', models.Contrataciones.fecha_bue_pro) == 2015,
                    models.Contrataciones.tipo_moneda == 'S/.'
                    )
            ).first()


    irregulares = (cont_irre * 100 ) / contratos

    return render_template(
        'index.html',
        top=top,
        contratos=contratos,
        empresas=empresas,
        entidades=entidades,
        proveedores=proveedores,
        irregulares=irregulares,
        total=total,
        topentidades=topentidades,
        totalsoles=total_soles
    )

def topEmpresas(anio):

    empresas = g.db.query(
                    models.Empresa.id,
                    models.Empresa.razon_social,
                    func.count(models.Contrataciones.empresa_id).label("cant")
                ).join(
                    models.Contrataciones
                ).filter(
                    extract('year', models.Contrataciones.fecha_bue_pro).label("anio") == anio
                ).order_by(
                    func.count(models.Contrataciones.empresa_id).desc()
                ).group_by(
                        models.Empresa.id
                ).limit(15)

    return empresas


def topEntidades(anio):

    entidades = g.db.query(
                    models.EntidadGobierno.id,
                    models.EntidadGobierno.nombre,
                    func.count(models.Contrataciones.entidad_id).label("cant")
                ).join(
                    models.Contrataciones
                ).order_by(
                    func.count(models.Contrataciones.entidad_id).desc()
                ).filter(
                    extract('year', models.Contrataciones.fecha_bue_pro).label("anio") == anio
                ).group_by(
                        models.EntidadGobierno.id
                ).limit(15)

    return entidades

@app.route('/buscar/<string:type>/', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/buscar/<string:type>/<int:page>', methods=['GET', 'POST'])
def buscar(type, page):
    
    form = SearchTerm(request.form)
    
    searchObj = search.Search()
    
    limit = 25

    termino = 'none'

    if request.args.get('termino'):
            
        termino = request.args.get('termino')
    
    if type == "contratos":

        contrataciones, pagination = searchObj.get_results_contrataciones(termino, page, limit)

        if termino == 'none':
            termino = ''
        
        return render_template(
            'buscar.html',
            termino=termino,
            pagination=pagination,
            contrataciones=contrataciones,
        )

    elif type == "entidades":

        entidades, pagination = searchObj.get_results_entidades(termino, page, limit)

        if termino == 'none':
            termino = ''

        return render_template(
            'buscar_entidad.html',
            termino=termino,
            pagination=pagination,
            entidades=entidades
        )

    elif type == "irregulares":

        irregulares, pagination = searchObj.get_results_irregulares(termino, page, limit)

        if termino == 'none':
            termino = ''

        return render_template(
            'buscar_irregulares.html',
            pagination=pagination,
            irregulares=irregulares,
            termino=termino
        )


    else:

        empresas, pagination = searchObj.get_results_empresas(termino, page, limit)

        if termino == 'none':
            termino = ''

        return render_template(
            'buscar_empresa.html',
            termino=termino,
            pagination=pagination,
            empresas=empresas
        )

@app.route('/entidad/<int:id>', methods=['GET', 'POST'])
def entidad(id):

    form = SearchFormEntidad()

    searchObj = advance_search.AdvanceSearchEntidad()

    entidad = g.db.query(
        models.EntidadGobierno.id,
        models.EntidadGobierno.nombre,
        models.TipoGobierno.tipo,
    ).join(
            models.TipoGobierno
    ).filter(
        models.EntidadGobierno.id == id
    ).first()

    page = 1

    if form.page.data:
        page = int(form.page.data)
            
    entidad.contrataciones, pagination = searchObj.get_results_contrataciones(id, form, page, 25)
    entidad.max = searchObj.get_max_ammount(id, form)
    entidad.min = searchObj.get_min_ammount(id, form)

    return render_template(
        'entidad.html',
        entidad=entidad,
        pagination=pagination,
        form=form,
    )


@app.route('/contrato/<int:id>', methods=['GET', 'POST'])
def contrato(id):

    contrato = g.db.query(
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
        models.Contrataciones.empresa_id,
        models.Empresa.razon_social,
        models.Empresa.ruc,
        models.Contrataciones.detalle_contrato,
        models.Contrataciones.detalle_seace,
        models.EntidadGobierno.tipo_gobierno_id,
        models.TipoGobierno.tipo,
        models.Contrataciones.entidad_id,
        models.EntidadGobierno.nombre,
    ).join(
        models.Empresa,
        models.EntidadGobierno,
        models.TipoGobierno
    ).filter(
        models.Contrataciones.id == id
    ).first()

    return render_template(
        'contrato.html',
        contrato=contrato,
    )


@app.route('/proveedor/<int:id>', methods=['GET', 'POST'])
def proveedor(id):

    form = SearchFormProveedor()

    searchObj = advance_search.AdvanceSearch()
        
    proveedor = g.db.query(
        models.Empresa
        ).filter(models.Empresa.id == id).first()

    page = 1

    if form.page.data:
        page = int(form.page.data)
            
    proveedor.contrataciones, pagination = searchObj.get_results_contrataciones(id, form, page, 25)
    proveedor.max = searchObj.get_max_ammount(id, form)
    proveedor.min = searchObj.get_min_ammount(id, form)

    return render_template(
    'proveedor.html',
     proveedor=proveedor,
     pagination=pagination,
     form=form
    )


@app.route('/api/get/search/<string:type>', methods=['GET'])
def get_search(type):
    termino = request.args.get('term')
    searchObj = search.Search()
    entidades, pagination = searchObj.get_results_contrataciones(termino, 1, 5)

    list = []

    for e in entidades:
        list.append(e.descripcion)

    return json.dumps(list)

if __name__ == '__main__':
    app.run(
        debug=settings.DEBUG,
    )

