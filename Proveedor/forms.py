from wtforms import Form, TextField
from wtforms.validators import Required, URL


class Search(Form):
    termino = TextField('Termino de busqueda', validators=[
        Required('Campo requerido')
    ])