# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from pybel.constants import IDENTIFIER, IS_A, NAME, PROTEIN
from .constants import EXPASY, MODULE_NAME, UNIPROT
from .models import Base, Enzyme, Prosite, Protein
from .parser.database import *
from .parser.tree import get_tree, give_edge, standard_ec_id
from .utils import check_namespaces

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

        #: Maps canonicalized ExPASy enzyme identifiers to their SQLAlchemy models
        self.id_enzyme = {}

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

    def get_or_create_enzyme(self, expasy_id, description=None):
        """Gets an enzyme from the database or creates it

        :param str expasy_id:
        :param Optional[str] description:
        :rtype: Enzyme
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            enzyme = Enzyme(
                expasy_id=expasy_id,
                description=description
            )
            self.session.add(enzyme)

        return enzyme

    def populate(self, tree_path=None, database_path=None):
        """Populates everything"""
        self.populate_tree(path=tree_path)
        self.populate_database(path=database_path)

    def populate_tree(self, path=None, cache=True, force_download=False):
        """Downloads and populates the expasy tree

        :param Optional[str] path: A custom url to download
        :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
        :param bool force_download: If true, overwrites a previously cached file
        """
        tree = get_tree(path=path, force_download=force_download)

        for expasy_id, data in tqdm(tree.nodes_iter(data=True), desc='Classes', total=tree.number_of_nodes()):
            enzyme = self.id_enzyme[expasy_id] = Enzyme(
                expasy_id=expasy_id,
                description=data['description']
            )
            self.session.add(enzyme)

        for parent_id, child_id in tqdm(tree.edges_iter(), desc='Tree', total=tree.number_of_edges()):
            parent = self.id_enzyme[parent_id]
            child = self.id_enzyme[child_id]
            parent.children.append(child)

        log.info("committing")
        self.session.commit()

    def populate_database(self, path=None, cache=True, force_download=False):
        """Populates the ExPASy database.

        :param Optional[str] path: A custom url to download
        :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
        :param bool force_download: If true, overwrites a previously cached file
        """
        data_dict = get_expasy_database(path=path, force_download=force_download)

        id_prosite = {}
        id_uniprot = {}

        for data_cell in tqdm(data_dict, desc='Database'):
            if data_cell['DELETED'] or data_cell['TRANSFERRED']:
                continue  # if both are false then proceed

            expasy_id = data_cell[ID]

            enzyme = self.id_enzyme[expasy_id] = Enzyme(
                expasy_id=expasy_id,
                description=data_cell[DE]
            )

            self.session.add(enzyme)

            parent_id, _ = give_edge(data_cell[ID])
            enzyme.parent = self.get_enzyme_by_id(parent_id)

            for prosite_id in data_cell.get(PR, []):
                prosite = id_prosite.get(prosite_id)

                if prosite is None:
                    prosite = id_prosite[prosite_id] = Prosite(prosite_id=prosite_id)
                    self.session.add(prosite)

                enzyme.prosites.append(prosite)

            for uniprot_data in data_cell.get(DR, []):
                up_tup = accession_number, entry_name = uniprot_data['accession_number'], uniprot_data['entry_name']
                protein = id_uniprot.get(up_tup)

                if protein is None:
                    protein = id_uniprot[up_tup] = Protein(
                        accession_number=accession_number,
                        entry_name=entry_name,
                    )
                    self.session.add(protein)

                enzyme.proteins.append(protein)

        log.info("committing")
        self.session.commit()

    def get_enzyme_by_id(self, expasy_id):
        """Gets an enzyme by its ExPASy identifier.
        
        Implementation note: canonicalizes identifier to remove all spaces first.

        :param str expasy_id: An ExPASy identifier. Example: 1.3.3.- or 1.3.3.19
        :rtype: Optional[Enzyme]
        """
        canonical_expasy_id = standard_ec_id(expasy_id)
        return self.session.query(Enzyme).filter(Enzyme.expasy_id == canonical_expasy_id).one_or_none()

    def get_parent(self, expasy_id):
        """Returns the parent ID of ExPASy identifier if exist otherwise returns None

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[Enzyme]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.parent

    def get_children(self, expasy_id):
        """Returns list of enzymes which are children of the enzyme with the given ExPASy enzyme identifier

        :param str expasy_id: An ExPASy enzyme identifier
        :rtype: Optional[list[Enzyme]]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.children

    def get_protein_by_uniprot_id(self, uniprot_id):
        """Gets a protein having the given UniProt identifier

        :param str uniprot_id: A UniProt identifier
        :rtype: Optional[Protein]

        >>> from bio2bel_expasy import Manager
        >>> manager = Manager()
        >>> protein = manager.get_protein_by_uniprot_id('Q6AZW2')
        >>> protein.accession_number
        'Q6AZW2'
        """
        return self.session.query(Protein).filter(Protein.accession_number == uniprot_id).one_or_none()

    def get_prosite_by_id(self, prosite_id):
        """Gets a ProSite having the given ProSite identifier

        :param str prosite_id: A ProSite identifier
        :rtype: Optional[Enzyme]
        """
        return self.session.query(Prosite).filter(Prosite.prosite_id == prosite_id).one_or_none()

    def get_prosite(self, expasy_id):
        """Gets a list of ProSites associated with the enzyme corresponding to the given identifier

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[list[Enzyme]]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.prosites

    def get_enzymes_by_prosite_id(self, prosite_id):
        """Returns Enzyme ID lists associated with the given ProSite ID

        :param str prosite_id: ProSite identifier
        :rtype: Optional[list[Enzyme]]
        """
        prosite = self.get_prosite_by_id(prosite_id)

        if prosite is None:
            return

        return prosite.enzymes

    def get_proteins_by_expasy_id(self, expasy_id):
        """Returns list of UniProt entries as tuples (accession_number, entry_name) of the given enzyme _id

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[list[Protein]]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.proteins

    def get_enzymes_by_uniprot_id(self, uniprot_id):
        """Returns a list of enzymes annotated to the protein with the given UniProt accession number.

        :param str uniprot_id: A UniProt identifier
        :rtype: Optional[list[Enzyme]]

        Example:

        >>> from bio2bel_expasy import Manager
        >>> manager = Manager()
        >>> manager.get_enzymes_by_uniprot_id('Q6AZW2')
        >>> ...
        """
        protein = self.get_protein_by_uniprot_id(uniprot_id)

        if protein is None:
            return

        return protein.enzymes

    def enrich_proteins(self, graph):
        """Enriches proteins in the BEL graph with IS_A relations to their enzyme classes.

        1. Gets a list of UniProt proteins
        2. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            if not check_namespaces(data, PROTEIN, EXPASY):
                continue
            proteins = self.get_proteins_by_expasy_id(data[NAME])

            if not proteins:
                log.warning("enrich_proteins():Unable to find node: %s", node)
                continue
            for prot in proteins:
                protein_tuple = graph.add_node_from_data(prot.serialize_to_bel())
                graph.add_unqualified_edge(node, protein_tuple, IS_A)

        for node, data in graph.nodes(data=True):
            if not check_namespaces(data, PROTEIN, UNIPROT):
                continue
            enzymes = self.get_enzymes_by_uniprot_id(data[IDENTIFIER])
            if not enzymes:
                log.warning("enrich_proteins(): no expasy entry for %s", node)
                continue
            for expasy in enzymes:
                expasy_tuple = graph.add_node_from_data(expasy.serialize_to_bel())
                graph.add_unqualified_edge(expasy_tuple, node, IS_A)

    def enrich_enzymes(self, graph):
        """Add all children of entries (enzyme codes with 4 numbers in them that can be directly annotated to proteins)

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            if not check_namespaces(data, PROTEIN, EXPASY):
                continue

            parent = self.get_parent(data[NAME])
            if parent:
                parent_tuple = graph.add_node_from_data(parent.serialize_to_bel())
                graph.add_unqualified_edge(parent_tuple, node, IS_A)
            else:
                log.warning('No parent node found for node %s', node)

            children_list = self.get_children(data[NAME])
            if not children_list:
                log.warning('No child node found for node %s', node)
                continue
            for child in children_list:
                expasy_tuple = graph.add_node_from_data(child.serialize_to_bel())
                graph.add_unqualified_edge(node, expasy_tuple, IS_A)

        self.enrich_proteins(graph=graph)
        self.enrich_prosites(graph=graph)

    def enrich_prosites(self, graph):
        """enriches Enzyme classes for ProSite in the graph.

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            if not check_namespaces(data, PROTEIN, EXPASY):
                continue
            prosite_list = self.get_prosite(data[NAME])
            if not prosite_list:
                log.warning('enrich_prosite_classes():Unable to find node %s', node)
                continue
            for prosite in prosite_list:
                prosite_tuple = graph.add_node_from_data(prosite.serialize_to_bel())
                graph.add_unqualified_edge(node, prosite_tuple, IS_A)
