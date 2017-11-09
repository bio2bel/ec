# -*- coding: utf-8 -*-

import os
import configparser
import logging
log = logging.getLogger(__name__)
log.setLevel(20)
logging.basicConfig(level=20)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .enzyme import *
from .tree import populate_tree
from .models import Base, Enzyme_Entry, Prosite_Entry, Protein_Entry
from .constants import ENZCLASS_CONFIG_FILE_PATH, ENZCLASS_SQLITE_PATH

class Manager(object):
    """Creates a connection to database and a persistient session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param str connection: SQLAlchemy
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        self.connection = self.get_connection_string(connection)
        self.engine = create_engine(self.connection, echo=echo)
        self.sessionmaker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = scoped_session(self.sessionmaker)
        self.create_tables()

    def create_tables(self, check_first=True):
        """creates all tables from models in your database

        :param bool check_first: True or False check if tables already exists
        """
        log.info('create tables in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_tables(self):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine)

    @staticmethod
    def get_connection_string(connection=None):
        """Return the SQLAlchemy connection string if it is set

        :param connection: get the SQLAlchemy connection string
        :rtype: str
        """
        if connection:
            return connection

        config = configparser.ConfigParser()

        cfp = ENZCLASS_CONFIG_FILE_PATH

        if os.path.exists(cfp):
            log.info('fetch database configuration from {}'.format(cfp))
            config.read(cfp)
            connection = config['database']['sqlalchemy_connection_string']
            log.info('load connection string from {}: {}'.format(cfp, connection))
            return connection

        with open(cfp, 'w') as config_file:
            config['database'] = {'sqlalchemy_connection_string': ENZCLASS_SQLITE_PATH}
            config.write(config_file)
            log.info('create configuration file {}'.format(cfp))

        return ENZCLASS_SQLITE_PATH

    def populate(self, force_download=False):
        """Populates the database

        :param bool force_download: Should the data be downloaded again, or cache used if exists?
        """
        tree_graph = populate_tree(force_download=force_download)
        data_dict = expasy_parser(force_download=force_download)

        id_model = {}

        for data_cell in data_dict:
            if not (data_cell['DELETED'] or data_cell['TRANSFERRED']):  # if both are false then proceed
                enzyme_entry = Enzyme_Entry(enzyme_id=data_cell[ID], description=data_cell[DE])
                self.session.add(enzyme_entry)
                id_model[data_cell[ID]] = enzyme_entry
                if data_cell[PR]:
                    for pr_id in data_cell[PR]:
                        prosite_entry = Prosite_Entry(prosite_id=pr_id, enzyme_id=data_cell[ID])
                        self.session.add(prosite_entry)
                if data_cell[DR]:
                    for dr_id in data_cell[DR]:
                        protein_entry = Protein_Entry(
                            enzyme_id=data_cell[ID],
                            AC_Nb=dr_id['AC_Nb'],
                            Entry_name=dr_id['Entry_name'],
                            #  is_SwissProt=
                        )
                        self.session.add(protein_entry)

        #TODO 3 add hierarchy data from tree_graph
            #for parent, child in tree_graph.edges_iter():
                #id_model[parent].children.append(id_model[child])
        self.session.commit()
        pass #TODO finish 3