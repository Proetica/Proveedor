#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import urllib
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import settings
import models
import re
import datetime

db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

db = sessionmaker(bind=db_engine)()


class importRepresentante():

    def scrapper(self, ruc):

        domain = "http://ww1.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"

        values = {'accion': 'getRepLeg',
                  'nroRuc': ruc,
                  'desRuc': ''
                  }

        try:
            data = urllib.urlencode(values)

            response = urllib2.urlopen(domain, data)

            content = BeautifulSoup(
                response.read(),
                'html.parser').findAll("table")

            rows = content[1].findAll("tr")

            representantes = []

            del rows[0]
            del rows[1]

            for cells in rows:
                datos = []
                for cell in cells.findAll("td"):
                    td = cell.getText().encode('UTF-8')
                    td = td.replace('\xc3\x91','Ñ')
                    match = re.search('Fecha', td)
                    if not match:
                        td = td.replace("   ", "").strip()
                        td = td.replace("\n", "")

                        datos.append(td)

                        representantes.append(datos)

            return representantes

        except:
            pass

    def save(self, ruc, id):
        personas = self.scrapper(ruc)
        _representante = models.Persona()
        representantes = []
        for persona in personas:
            if db.query(
                models.Persona.id
            ).filter(
                models.Persona.dni == persona[1]
            ).count() == 0:                
                _representante.dni = persona[1]
                _representante.nombre = persona[2].decode('utf-8')

                db.add(_representante)

                try:
                    db.commit()
                except:
                    db.rollback()

            if db.query(
                models.Empresa_persona
            ).filter(
                and_(models.Empresa_persona.empresa_id == id,
                     models.Empresa_persona.persona_id == _representante.id,
                     models.Empresa_persona.cargo == persona[3])
            ).count() == 0:
                _empresa_persona = models.Empresa_persona()
                _empresa_persona.empresa_id = id
                _empresa_persona.persona_id = _representante.id
                _empresa_persona.cargo = persona[3]
                _empresa_persona.fecha_cargo = datetime.datetime.strptime(persona[4], '%d/%m/%Y')

                db.add(_empresa_persona)

                try:
                    db.commit()                       
                except:
                    db.rollback()        
        return 'ok'


if __name__ == '__main__':
    importRepresentante().scrapper('20525391966')
