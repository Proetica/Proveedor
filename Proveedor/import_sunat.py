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

db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

db = sessionmaker(bind=db_engine)()


class importSunat():

    def scrapper(self, ruc):

        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket

        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        domain = "http://ww1.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"

        values = {'accion': 'consPorRuc',
                  'actReturn': '1',
                  'nroRuc': ruc,
                  'numRnd': '1144429091'
                  }

        data = urllib.urlencode(values)

        response = opener.open(domain, data)

        print response.read()

        content = BeautifulSoup(
            response.read(),
            'html.parser').find("table", {'class', 'form-table'})

        rows = content.findAll("tr")

        direccion = rows[6].getText().encode('UTF-8')

        return direccion

    def save(self, ruc):

        empresa = db.query(
            models.Empresa.direccion
        ).filter(
            models.Empresa.ruc == ruc
        ).first()

        if(empresa.direccion is ''):
            direccion = self.scrapper(ruc)
            empresa.direccion = direccion
            db.add(empresa)

            try:
                db.commit()
            except:
                db.rollback()

        return direccion


if __name__ == '__main__':
    importSunat().scrapper('20494139988')
