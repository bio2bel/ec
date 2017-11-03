# -*- coding: utf-8 -*-

import os
import configparser
import logging
log = logging.getLogger(__name__)
log.setLevel(20)
logging.basicConfig(level=20)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .enzyme import expasy_parser
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

