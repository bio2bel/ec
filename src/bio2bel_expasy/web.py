# -*- coding: utf-8 -*-

""" This module contains the flask application to visualize the db

when pip installing

.. source-code:: sh

    pip install bio2bel_chebi[web]

"""

import flask_admin
from flask import Flask
from flask_admin.contrib.sqla import ModelView

from .database import Manager
from .models import *

app = Flask(__name__)
admin = flask_admin.Admin(app, url='/')

manager = Manager()


class EnzymeView(ModelView):
    column_hide_backrefs = False
    column_list = ('expasy_id', 'description', 'parents')


admin.add_view(EnzymeView(Enzyme, manager.session))
admin.add_view(ModelView(Prosite, manager.session))
admin.add_view(ModelView(Protein, manager.session))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
