#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as Soup
import urllib2
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import settings
import models
import datetime
import re


db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

db = sessionmaker(bind=db_engine)()


def scrapper(eid):

    domain = "http://www.peru.gob.pe/transparencia/pep_transparencia.asp?Tipo_Pod=%s" % eid
    response = urllib2.urlopen(domain)
    content = Soup(response.read(), 'html.parser').find("ul", {'class', 'tree'})
    lifirst = content.find("ul");

    _tipo_entidad = models.TipoEntidadGobierno()

    for li in lifirst.findAll("a"):        
        nombre = li.get_text()
        href = li['href']
        href = href.replace('pep_transparencia_lista_planes.asp?id_entidad=','')
        href = href.replace('&id_tema=1&ui=12','')

        if db.query(
            models.EntidadGobierno.id
        ).filter(                
            models.EntidadGobierno.id == href
        ).count() == 0:
            _entidad = models.EntidadGobierno()
            _entidad.id = href
            _entidad.nombre = nombre
            _entidad.tipo_gobierno_id = eid
            db.add(_entidad)
            db.commit()


if __name__ == '__main__':

    for i in [1,3]:
        scrapper(i)