# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from .constants import MODULE_NAME
from .enzyme import *
from .models import Base, Enzyme, Prosite, Protein
from .tree import edge_description, give_edge, populate_tree, standard_ec_id

log = logging.getLogger(__name__)


class Manager(object):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param str connection: SQLAlchemy
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        self.connection = get_connection(MODULE_NAME, connection=connection)
        log.info('using connection %s', connection)
        self.engine = create_engine(self.connection, echo=echo)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = scoped_session(self.session_maker)
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
    def ensure(connection=None):
        """Checks and allows for a Manager to be passed to the function.

        :param connection: can be either a already build manager or a connection string to build a manager with.
        """
        if connection is None or isinstance(connection, str):
            return Manager(connection=connection)

        if isinstance(connection, Manager):
            return connection

        raise TypeError

    def populate(self, force_download=False):
        """Populates the database

        :param bool force_download: Should the data be downloaded again, or cache used if exists?
        """
        data_dict = expasy_parser(force_download=force_download)
        tree_graph = populate_tree(force_download=force_download)

        id_enzyme = {}
        id_prosite = {}
        id_protein = {}

        for data_cell in tqdm(data_dict, desc='ExPASy'):
            if not (data_cell['DELETED'] or data_cell['TRANSFERRED']):  # if both are false then proceed
                enzyme_entry = Enzyme(
                    expasy_id=data_cell[ID],
                    description=data_cell[DE]
                )

                self.session.add(enzyme_entry)
                id_enzyme[data_cell[ID]] = enzyme_entry
                parent_id = give_edge(data_cell[ID])[0]
                child_id = data_cell[ID]
                while (parent_id):
                    if parent_id not in id_enzyme.keys():
                        enzyme_parent_entry = Enzyme(
                            expasy_id=parent_id,
                            description=edge_description(parent_id)
                        )
                        self.session.add(enzyme_parent_entry)
                        id_enzyme[parent_id] = enzyme_parent_entry
                        id_enzyme[parent_id].children.append(id_enzyme[child_id])
                    else:
                        id_enzyme[parent_id].children.append(id_enzyme[child_id])

                    child_id = parent_id
                    parent_id = give_edge(parent_id)[0]

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

                        accession_number = dr_id['accession_number']
                        entry_name = dr_id['entry_name']

                        if (accession_number, entry_name) not in id_protein:
                            protein_entry = Protein(
                                accession_number=accession_number,
                                entry_name=entry_name,
                                #  is_SwissProt=
                            )
                            id_protein[accession_number, entry_name] = protein_entry
                            self.session.add(protein_entry)
                        else:
                            protein_entry = id_protein[accession_number, entry_name]

                        enzyme_entry.proteins.append(protein_entry)

        log.info("\nBuilding (Committing) DataBase ...\n")

        self.session.commit()

    def get_enzyme_by_id(self, expasy_id):
        """Gets an enzyme by its ExPAsY identifier.
        
        Implementation note: canonicalizes identifier to remove all spaces first.

        :param str expasy_id: The ExPAsY database identifier. Example: 1.3.3.- or 1.3.3.19
        :rtype: Optional[Enzyme]
        """
        canonical_expasy_id = standard_ec_id(expasy_id)
        return self.session.query(Enzyme).filter(Enzyme.expasy_id == canonical_expasy_id).one_or_none()

    def get_protein_by_id(self, uniprot_id):
        """Returns protein entry for given UniProt identifier

        :param str uniprot_id: A UniProt identifier
        :rtype: Optional[Protein]
        """
        return self.session.query(Protein).filter(uniprot_id == Protein.accession_number).one_or_none()

    def get_prosite_by_id(self, prosite_id):
        """Returns ProSite entry for given ProSite identifier

        :param prosite_id:
        :rtype: Optional[Enzyme]
        """
        return self.session.query(Prosite).filter(prosite_id == Prosite.prosite_id).one_or_none()

    def get_parent(self, expasy_id):
        """Returns the parent ID of ExPASy identifier if exist otherwise returns None

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[Enzyme]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.parent

    def get_description(self, expasy_id):
        """Return the Description of the enzyme, None if doesn't exist

        :param str expasy_id: An ExPASy identifier
        :rtype: str
        """

        return self.session.query(Enzyme.description).filter_by(expasy_id=expasy_id).first()[0]

    def get_prosite(self, expasy_id):
        """Returns list of Prosite ID's associated with the given Enzyme ID

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[list[Enzyme]]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.prosites

    def get_expasy_form_prosite(self, prosite_id):
        """Returns Enzyme ID lists associated with the given ProSite ID

        :param str prosite_id: ProSite identifier
        :rtype: Optional[list[Enzyme]]
        """
        prosite = self.get_prosite_by_id(prosite_id)

        if prosite is None:
            return

        return prosite.enzymes

    def get_uniprot(self, expasy_id):
        """Returns list of UniProt entries as tuples (accession_number, entry_name) of the given enzyme _id

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[list[Protein]]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.proteins

    def get_expasy_from_uniprot(self, uniprot_id):
        """Returns Enzyme ID list associated with the given uniprot accession_number

        :param str uniprot_id: A UniProt identifier
        :rtype: Optional[list[Enzyme]]
        """
        protein = self.get_protein_by_id(uniprot_id)

        if protein is None:
            return

        return protein.enzymes

    def get_children(self, expasy_id):
        """Returns list of Expasy ID's which are children for given Expasy _id

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[list[Enzyme]]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.children
