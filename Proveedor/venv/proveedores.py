#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import urllib
from cookielib import CookieJar
import socks
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings
import models
import datetime

domain = "http://apps5.mineco.gob.pe/proveedor/PageTop.aspx"

domain_detalle = "http://www.razonsocialperu.com/empresa/detalle/"

db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

db = sessionmaker(bind=db_engine)()


def scrapper(page):

    values = {'__EVENTTARGET': '',
              '__EVENTARGUMENT': '',
              '__VIEWSTATE': '/wEPDwUJODA2Mjc5NjYwDxYEHghPcmRlckRpcgEBAB4IU2VhcmNoQnkLKVtwcm92ZWVkb3IuU2VhcmNoQnksIHByb3ZlZWRvciwgVmVyc2lvbj0xLjAuNTI3NS4yNjQ5MywgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1udWxsABYCZg9kFgQCCw8PFgQeCFJvd0NvdW50At+nGh4HVmlzaWJsZWdkFgQCCQ8WAh4EVGV4dAUyPGI+MTwvYj4gLSA8Yj4yNTA8L2I+IGRlIDxiPjQzMSwwNzE8L2I+IHJlc3VsdGFkb3NkAg0PFgIfBAUMPGI+MSw3MjU8L2I+ZAINDxYCHwNnFgICAw9kFgJmD2QWAgIHDw8WAh8DaGRkZEIgsWQML4bShDwnYoDqufHkVWdi8DesHGSmS1MpCDVb',
              '__EVENTVALIDATION': '/wEdAA+oy/EtT2tk5Wj9bfH7JVrjQ/XnI9JNF8oTY7w8H74w/LPTnR9fOc03xnlp6oT8D8NAwiWIc3ifkY498zcTyDajL8NI3r2BJTed5JhUovWhgQyif6KZc1ESStxnceVeoJ6nfZhfGvB9pDnYk8R04DlDyf3bBtJAsREOSv6Bv5NrawDTwwPrxtqjWLIH1uyteWYkhML6BNfAbMNMh70eHArj4Invb0MbNvZAoosAssfcaRNQgFrBJLXW9t9Im8DSBQZB75oOuKkKInsq/TeFqNARJNHCZxrfWXDJZ+50rUXWXykeI6z8FCyClAytDBydSh5htRMgF3esqDbacE/0eau57Rirxs/hWcBcunD9X96Ycw==',
              'Pager1:TxtPage': page,
              'TxtBuscar': '',
              'hFiltros': '',
              'hAgrupacion': '9',
              'hAntAgrupacion': '9',
              'hHistorico': '0/9',
              'hPostedBy': '0'}

    data = urllib.urlencode(values)
    response = urllib2.urlopen(domain, data)
    content = BeautifulSoup(response.read(), 'html.parser').find("table", {'class', 'Data'})

    for r in content.findAll("tr"):

        cells = r.findAll("td")
        d = cells[1].getText().encode('utf-8')
        item = d.split(":")
        ruc = ((item[0]).strip()).replace('\xc2\xa0', '')
        rs = ((item[1]).strip())
        total = float((cells[2].getText()).replace(",", ""))

        detalles = urllib2.urlopen(domain_detalle + ruc)

        detalles_content = BeautifulSoup(detalles.read(), 'html.parser')

        detalles_content = detalles_content.findAll("table")

        detalles = detalles_content[0].findAll("tr")

        if db.query(
            models.Empresa
        ).filter(
            models.Empresa.ruc == ruc
        ).count() == 0:
            _entry = models.Empresa()
            _entry.ruc = ruc
            _entry.razon_social = rs
            _entry.total_ganado = total

            print detalles_content[0]

            if detalles[2].find("td").getText():
                _entry.nombre_comercial = detalles[2].find("td").getText()
                _entry.inicio_actividades = datetime.datetime.strptime(
                    detalles[4].find("td").getText(), '%d/%m/%Y')
                _entry.actividades_com_ext = detalles[5].find("td").getText()
                _entry.telefono = detalles[7].find("td").getText()
                _entry.fax = detalles[8].find("td").getText()
                _entry.estado = detalles[9].find("td").getText()
                _entry.condicion = detalles[10].find("td").getText()
                _entry.direccion = detalles[6].find("td").getText()
                _entry.update = 1

            db.add(_entry)

            try:
                db.commit()
            except:
                db.rollback()

            if len(detalles_content) == 2:
                sucursales = detalles_content[1].findAll("tr")
                if sucursales is not None:
                    for _cell in sucursales:
                        sucursal = []
                        sucursal = _cell.find("td")    
                        try:
                            _sucursal = models.Sucursal()
                            _sucursal.empresa_id = _entry.id
                            _sucursal.tipo = sucursal[1].getText()
                            _sucursal.direccion = sucursal[2].getText()
                            db.add(_sucursal)
                        except:
                            pass

                        try:
                            db.commit()
                        except:
                            db.rollback()


if __name__ == '__main__':

    for i in range(1,3):
        scrapper(i)