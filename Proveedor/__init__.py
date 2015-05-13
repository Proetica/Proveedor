from flask import Flask, g, render_template, url_for, request, redirect
from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import models, forms, settings
import search
import json

app = Flask(
    __name__,
    static_folder=settings.STATIC_PATH,
    static_url_path=settings.STATIC_URL_PATH
)
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

    top = g.db.query(
                models.Empresa.id,
                models.Empresa.razon_social,
                func.count(models.Contrataciones.empresa_id).label("cant")
            ).outerjoin(
                models.Contrataciones
            ).order_by(
                func.count(models.Contrataciones.empresa_id).desc()
            ).group_by(
                    models.Empresa.id
            ).limit(15)

    topentidades = g.db.query(
                models.EntidadGobierno.id,
                models.EntidadGobierno.nombre,
                func.count(models.Contrataciones.entidad_id).label("cant")
            ).outerjoin(
                models.Contrataciones
            ).order_by(
                func.count(models.Contrataciones.entidad_id).desc()
            ).group_by(
                    models.EntidadGobierno.id
            ).limit(15)

    contratos = g.db.query(
                models.Contrataciones
            ).count()

    empresas = g.db.query(
                models.Empresa
            ).count()

    entidades = g.db.query(
                models.EntidadGobierno
            ).count()

    cont_irre = g.db.query(
                models.Contrataciones
            ).filter(
                or_(models.Contrataciones.etiqueta_fecha == 'Fechas cercanas',
                    models.Contrataciones.etiqueta_fecha == 'Fechas coinciden')
            ).count()

    total = g.db.query(
                func.sum(models.Contrataciones.monto).label("total")
            ).filter(
                models.Contrataciones.tipo_moneda == 'S/. '
            ).first()

    irregulares = 0 #(cont_irre * 100 ) / contratos

    return render_template(
        'index.html',
        top=top,
        contratos=contratos,
        empresas=empresas,
        entidades=entidades,
        irregulares=irregulares,
        total=total,
        topentidades=topentidades
    )

@app.route('/buscar/<string:type>', defaults={'termino':'', 'page':1}, methods=['GET', 'POST'])
@app.route('/buscar/<string:type>/<string:termino>/<int:page>', methods=['GET', 'POST'])
def buscar(type, termino, page):
    
    form = forms.Search(request.form)
    searchObj = search.Search()
    limit = 25

    if request.method == 'POST' and form.validate():
            
        termino = form.termino.data
    
    if type == "contratos":

        contrataciones, pagination = searchObj.get_results_contrataciones(termino, page, limit)
        
        return render_template(
            'buscar.html',
            termino=termino,
            pagination=pagination,
            contrataciones=contrataciones,
        )

    elif type == "entidades":

        entidades, pagination = searchObj.get_results_entidades(termino, page, limit)

        return render_template(
            'buscar_entidad.html',
            termino=termino,
            pagination=pagination,
            entidades=entidades
        )

    else:

        empresas, pagination = searchObj.get_results_empresas(termino, page, limit)

        return render_template(
            'buscar_empresa.html',
            termino=termino,
            pagination=pagination,
            empresas=empresas
        )


@app.route('/empresas', methods=['GET', 'POST'])
def empresas():

    proveedores = g.db.query(
        models.Empresa.id,
        models.Empresa.ruc,
        models.Empresa.razon_social,
        models.Empresa.total_ganado
    ).order_by(
        models.Empresa.total_ganado.desc()
    ).limit(200)

    return render_template(
        'empresas.html',
        proveedores=proveedores,
    )


@app.route('/entidades')
def entidades():

    entidades = g.db.query(
        models.EntidadGobierno.id,
        models.EntidadGobierno.nombre,
        models.TipoGobierno.tipo,
    ).join(
            models.TipoGobierno
    ).order_by(
        models.EntidadGobierno.nombre.asc()
    )

    return render_template(
        'entidades.html',
        entidades=entidades,
    )


@app.route('/entidad/<int:id>', methods=['GET', 'POST'])
def entidad(id):

    entidad = g.db.query(
        models.EntidadGobierno.id,
        models.EntidadGobierno.nombre,
        models.TipoGobierno.tipo,
    ).join(
            models.TipoGobierno
    ).filter(
        models.EntidadGobierno.id == id
    ).first()

    contrataciones = g.db.query(
        models.Contrataciones.id,
        models.Contrataciones.proceso,
        models.Contrataciones.objeto_pro,
        models.Contrataciones.fecha_pub,
        models.Contrataciones.fecha_bue_pro,
        models.Contrataciones.modalidad_sel,
        models.Contrataciones.tipo_moneda,
        models.Contrataciones.monto,
        models.Contrataciones.valor_ref,
        models.Contrataciones.descripcion,        
        models.Empresa.razon_social,
        models.Empresa.ruc,
        models.Contrataciones.detalle_contrato,
        models.Contrataciones.detalle_seace,
        models.Contrataciones.empresa_id
    ).join(
        models.Empresa
    ).filter(
        models.Contrataciones.entidad_id == id
    ).order_by(
         models.Empresa.ruc.desc()
    ).limit(25)

    return render_template(
        'entidad.html',
        entidad=entidad,
        contrataciones=contrataciones
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


    if request.form:
        form = request.form
        print form
        

    proveedor = g.db.query(
        models.Empresa
        ).filter(models.Empresa.id == id).first()


    if g.db.query(
            models.Load_empresa
        ).filter(
            models.Load_empresa.empresa_id == id
        ).count() == 0 and proveedor.ruc[:1] == 2:

            return render_template(
                'loadproveedor.html',
                proveedor=proveedor,
            )
            
    else:
        
        representantes = g.db.query(
            models.Empresa_persona
            ).filter(
            models.Empresa_persona.empresa_id == id
            ).order_by(
            models.Empresa_persona.fecha_cargo.desc()
            ).join(
            models.Persona
            ).values(
            models.Persona.id,
            models.Persona.dni,
            models.Persona.nombre,
            models.Empresa_persona.cargo,
            models.Empresa_persona.fecha_cargo)

        contrataciones = g.db.query(
            models.Contrataciones.id,
            models.Contrataciones.proceso,
            models.Contrataciones.objeto_pro,
            models.Contrataciones.fecha_pub,
            models.Contrataciones.fecha_bue_pro,
            models.Contrataciones.modalidad_sel,
            models.Contrataciones.tipo_moneda,
            models.Contrataciones.monto,
            models.Contrataciones.valor_ref,
            models.Contrataciones.descripcion,
            models.Contrataciones.entidad_id,
            models.EntidadGobierno.nombre,
            models.Contrataciones.detalle_contrato,
            models.Contrataciones.detalle_seace,
            models.Contrataciones.empresa_id,
            models.Empresa.razon_social
        ).join(
            models.EntidadGobierno,
            models.Empresa
        ).filter(
            models.Contrataciones.empresa_id == id
        ).order_by(
             models.Contrataciones.fecha_bue_pro.desc()
        ).limit(10)

        proveedor.representantes = representantes
        proveedor.contrataciones = contrataciones

        return render_template(
        'proveedor.html',
         proveedor=proveedor,
        )


@app.route('/api/get/proveedor/<int:id>', methods=['GET', 'POST'])
def get_proveedor(id):

    proveedor = g.db.query(
        models.Empresa
    ).filter(
        models.Empresa.id == id
    ).first()

    if (proveedor.ruc[:1] == 2):
        representanteClass = import_representante.importRepresentante()
        representantes = representanteClass.save(proveedor.ruc, id)

        proveedorDetail = import_proveedor_detail.importDetail()
        detail = proveedorDetail.scrapper(proveedor.ruc)

        load = models.Load_empresa()
        load.empresa_id = id

        g.db.add(load)

        try:
            g.db.commit()
        except:
            g.db.rollback()
    
        return '{0}-{1}'.format(representantes, detail)
    return '{0}-{1}'.format('ok', 'ok')


@app.route('/representante/<int:id>', methods=['GET', 'POST'])
def representante(id):

    representante = g.db.query(
        models.Persona
    ).filter(
        models.Persona.id == id
    ).first()

    empresas = g.db.query(
        models.Empresa_persona
    ).order_by(
            models.Empresa_persona.fecha_cargo.desc()
    ).filter(
        models.Empresa_persona.persona_id == id
    ).join(
        models.Persona,
        models.Empresa
    ).values(
        models.Empresa.id,
        models.Empresa.razon_social,
        models.Empresa.ruc,
        models.Empresa.total_ganado,
        models.Empresa_persona.cargo,
        models.Empresa_persona.fecha_cargo
    )

    representante.empresas = empresas

    return render_template(
        'representante.html',
        representante=representante,
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

