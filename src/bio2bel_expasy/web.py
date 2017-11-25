# -*- coding: utf-8 -*-

""" This module contains the flask application to visualize the db

when pip installing

.. source-code:: sh

    pip install bio2bel_expasy[web]

"""

import flask_admin
from flask import Flask
from flask_admin.contrib.sqla import ModelView

from bio2bel_expasy import Manager
from bio2bel_expasy.models import Enzyme, Prosite, Protein


class EnzymeView(ModelView):
    column_hide_backrefs = False
    column_list = ('expasy_id', 'description', 'parents')


def add_admin(app, session, **kwargs):
    admin = flask_admin.Admin(app, **kwargs)
    admin.add_view(EnzymeView(Enzyme, session))
    admin.add_view(ModelView(Prosite, session))
    admin.add_view(ModelView(Protein, session))
    return admin


def create_app(connection=None, url=None):
    """Creates a Flask application

    :type connection: Optional[str]
    :rtype: flask.Flask
    """
    app = Flask(__name__)
    manager = Manager(connection=connection)
    add_admin(app, manager.session, url=url)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
