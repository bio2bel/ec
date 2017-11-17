# -*- coding: utf-8 -*-

import configparser
import logging
import os

from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm

from .constants import CONFIG_FILE_PATH, DEFAULT_CACHE_CONNECTION
from .enzyme import *
from .models import Base, Enzyme, Prosite, Protein
from .tree import edge_descpription, give_edge, populate_tree

log = logging.getLogger(__name__)


class Manager(object):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param str connection: SQLAlchemy
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        self.connection = self.get_connection_string(connection)
        log.info('Using connection %s', connection)
        self.engine = create_engine(self.connection, echo=echo)
        self.sessionmaker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = scoped_session(self.sessionmaker)
        self.create_all()

    def create_all(self, check_first=True):
        """creates all tables from models in your database

        :param bool check_first: True or False check if tables already exists
        """
        log.info('create tables in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self):
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

        cfp = CONFIG_FILE_PATH

        if os.path.exists(cfp):
            log.info('fetch database configuration from {}'.format(cfp))
            config.read(cfp)
            connection = config['database']['sqlalchemy_connection_string']
            log.info('load connection string from {}: {}'.format(cfp, connection))
            return connection

        with open(cfp, 'w') as config_file:
            config['database'] = {'sqlalchemy_connection_string': DEFAULT_CACHE_CONNECTION}
            config.write(config_file)
            log.info('create configuration file {}'.format(cfp))

        return DEFAULT_CACHE_CONNECTION

    def populate(self, force_download=False):
        """Populates the database

        :param bool force_download: Should the data be downloaded again, or cache used if exists?
        """
        data_dict = expasy_parser(force_download=force_download)
        tree_graph = populate_tree(force_download=force_download)

        id_enzyme = {}
        id_prosite = {}
        id_protein = {}

        for data_cell in tqdm(data_dict, desc='ExPaSY'):
            if not (data_cell['DELETED'] or data_cell['TRANSFERRED']):  # if both are false then proceed
                enzyme_entry = Enzyme(
                    expasy_id=data_cell[ID],
                    description=data_cell[DE]
                )

                self.session.add(enzyme_entry)
                id_enzyme[data_cell[ID]] = enzyme_entry
                if give_edge(data_cell[ID])[0] not in id_enzyme.keys():
                    enzyme_parent_entry = Enzyme(
                        expasy_id=give_edge(data_cell[ID])[0],
                        description=edge_descpription(give_edge(data_cell[ID])[0])
                    )
                    self.session.add(enzyme_parent_entry)
                    id_enzyme[give_edge(data_cell[ID])[0]] = enzyme_parent_entry
                    # id_enzyme[data_cell[ID]].parent = id_enzyme[give_edge(data_cell[ID])[0]]
                    id_enzyme[give_edge(data_cell[ID])[0]].parent.append(id_enzyme[data_cell[ID]])
                else:
                    id_enzyme[give_edge(data_cell[ID])[0]].parent.append(id_enzyme[data_cell[ID]])

                if PR in data_cell and data_cell[PR]:
                    for pr_id in data_cell[PR]:

                        if pr_id not in id_prosite:
                            prosite_entry = Prosite(prosite_id=pr_id)
                            id_prosite[pr_id] = prosite_entry
                            self.session.add(prosite_entry)
                        else:
                            prosite_entry = id_prosite[pr_id]

                        enzyme_entry.prosites.append(prosite_entry)

                if DR in data_cell and data_cell[DR]:
                    for dr_id in data_cell[DR]:

                        ac_nb = dr_id['accession_number']
                        entry_name = dr_id['Entry_name']

                        if (ac_nb, entry_name) not in id_protein:
                            protein_entry = Protein(
                                accession_number=dr_id['accession_number'],
                                Entry_name=dr_id['Entry_name'],
                                #  is_SwissProt=
                            )
                            id_protein[ac_nb, entry_name] = protein_entry
                            self.session.add(protein_entry)
                        else:
                            protein_entry = id_protein[ac_nb, entry_name]

                        enzyme_entry.proteins.append(protein_entry)

        log.info("\nBuilding (Committing) DataBase ...\n")

        self.session.commit()

    def get_parent(self, _id):
        """Returns the parent ID of expasy_id if exist otherwise returns None

        :param str _id: ExPASy ID of enzyme which parent is needed
        :rtype str
        """

        #return self.session.query(Enzyme.expasy_id).filter(Enzyme.id == 2)
        #return self.session.query(Enzyme.expasy_id).filter(Enzyme.id in self.session.query(Enzyme.parent_id).filter(Enzyme.expasy_id == _id).one_or_none())
        return self.session.query(Enzyme.expasy_id).filter_by(id=self.session.query(Enzyme.parent_id).filter_by(expasy_id = _id).first()[0]).first()[0]

    def get_description(self, _id):
        """Return the Description of the enzyme, None if doesn't exist

        :param str _id: ExPASy ID of the enzyme which Description is needed
        :rtype str
        """

        return self.session.query(Enzyme.description).filter_by(expasy_id=_id).first()[0]

    def get_prosite(self, _id):
        """Returns list of Prosite ID's associated with the given Enzyme ID
        :param str _id: ExPASy ID
        :return: resulting list of strings
        """

        return [a[0] for a in self.session.query(Prosite.prosite_id).filter(Prosite.enzymes.any(Enzyme.expasy_id==_id)).all()]

    def get_expasy_form_prosite(self, _id):
        """Returns Enzyme ID lists associated with the given Proside ID

        :param str _id: Prosite ID
        :return: list of strings
        """

        return [a[0] for a in self.session.query(Enzyme.expasy_id).join(Enzyme, Prosite.enzymes).filter(Prosite.enzymes.any(Prosite.prosite_id==_id)).all()]

    def get_uniprot(self, _id):
        """Returns list of UniProt entries as tuples (accession_number, entry_name) of the given enzyme _id

        :param str _id:
        :return:
        """

        return [a for a in self.session.query(Protein.accession_number, Protein.Entry_name).filter(Protein.enzymes.any(Enzyme.expasy_id==_id)).all()]
