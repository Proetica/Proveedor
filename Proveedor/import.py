#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as Soup
import urllib2, urllib
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import settings, parse_numbers
import models
import datetime
import re, time
import socks
import socket
from cookielib import CookieJar


db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

db = sessionmaker(bind=db_engine)()

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

class ProveedoresTransparencia():

    def scrapper(self, id_entidad, anno, mes):

        values = { 'id_entidad': id_entidad,
                   'id_tema': 34,
                   'mes': 1,
                   'pk_anno': anno,
                   'cbo_mes': mes}


        try:
            domain = "http://www.peru.gob.pe/transparencia/pep_transparencia_osce.asp"
            data = urllib.urlencode(values)
            response = opener.open(domain, data)
            
            content = Soup(response.read(), 'html.parser').find("table", attrs={'bgcolor': '#135588'})

            if content is not None:
                rows = content.findAll('tr')
                del rows[0]
                for row in rows:
                    cell = row.findAll("td")

                    _empresa = db.query(
                            models.Empresa.id
                        ).filter(                
                            models.Empresa.ruc == cell[9].get_text()
                        ).first()

                    if db.query(
                            models.Empresa.id
                        ).filter(
                            models.Empresa.ruc == cell[9].get_text()
                        ).count() == 0:
                        _empresa = models.Empresa()
                        _empresa.ruc = cell[8].get_text()
                        _empresa.razon_social = cell[8].find("a").get_text()
                        _empresa.nombre_comercial = cell[8].find("a").get_text()
                        db.add(_empresa)
                        db.commit()

                    _contratacion = models.Contrataciones()
                    _contratacion.fecha_pub = cell[0].get_text().strip()
                    _contratacion.fecha_bue_pro = cell[6].get_text().strip()

                    if(_contratacion.fecha_pub == _contratacion.fecha_bue_pro):
                        _contratacion.etiqueta_fecha = "Fechas coinciden"

                    a = datetime.datetime.strptime(_contratacion.fecha_pub,'%d/%m/%Y')
                    b = datetime.datetime.strptime(_contratacion.fecha_bue_pro,'%d/%m/%Y')
                    delta = b - a
                    
                    if(delta.days <= 5):
                        _contratacion.etiqueta_fecha = "Fechas cercanas"


                    parseNumbers = parse_numbers.parseNumbers()
                    _contratacion.proceso = cell[1].get_text().strip()
                    _contratacion.objeto_pro = cell[2].get_text().strip()
                    _contratacion.descripcion = cell[3].get_text().strip()                        
                    _contratacion.valor_ref = parseNumbers.parse(cell[4].get_text().strip())
                    _contratacion.monto = parseNumbers.parse(cell[7].get_text().strip())
                    _contratacion.valor_ref_text = cell[4].get_text().strip()
                    _contratacion.monto_text = cell[7].get_text().strip()
                    _contratacion.tipo_moneda = parseNumbers.get_symbol(cell[7].get_text().strip())

                    if(_contratacion.valor_ref  <= _contratacion.monto ):
                        _contratacion.etiqueta_monto = "Monto de contrato mayor"

                    _contratacion.modalidad_sel = cell[5].get_text().strip()
                    _dcontrato = cell[8].find("a")['href'].replace("pep_js_abrir_sub_ventanas('","http://www.peru.gob.pe/transparencia/")
                    _dcontrato = _dcontrato.replace("Javascript: ","")
                    _dcontrato = _dcontrato.replace("','700','900')","")
                    _contratacion.detalle_contrato = _dcontrato
                    
                    try:
                        _contratacion.detalle_seace = cell[10].find("a")['href']
                    except:
                        _contratacion.detalle_seace = 'No hay referencia'

                    _contratacion.empresa_id = _empresa.id
                    _contratacion.entidad_id = id_entidad

                    db.add(_contratacion)                  

                    try:
                        db.commit()
                    except:
                        pass

            else:
                pass
        except socket.timeout, e:
            # For Python 2.7
            pass


    def get(self, eid, anno):
        #Extrac values by Entity
        for mes in range(1, 13):
            ProveedoresTransparencia().scrapper(eid, anno, mes)
            time.sleep(3)


if __name__ == '__main__':
    _entidades = db.query(models.EntidadGobierno).filter(
        models.EntidadGobierno.cargado==0
        ).all()
    for _entidad in _entidades:
        for anno in range(2009, 2016):
            for mes in range(1, 13):
                ProveedoresTransparencia().scrapper(_entidad.id, anno, mes)
        _entidad.cargado = 1
        db.add(_entidad)
        try:
            db.commit()
        except:
            pass
