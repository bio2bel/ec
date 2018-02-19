# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from pybel.constants import IDENTIFIER, IS_A, NAME, NAMESPACE, NAMESPACE_DOMAIN_GENE
from pybel.resources import write_namespace
from pybel.resources.arty import get_today_arty_namespace
from pybel.resources.deploy import deploy_namespace
from .constants import MODULE_NAME
from .models import Base, Enzyme, Prosite, Protein
from .parser.database import *
from .parser.tree import get_tree, give_edge, normalize_expasy_id

__all__ = ['Manager']

log = logging.getLogger(__name__)


def _write_bel_namespace_helper(values, file):
    """
    :param dict[str,str] values:
    :param file:
    """
    write_namespace(
        namespace_name='Enzyme Classes',
        namespace_keyword='EV',
        namespace_domain=NAMESPACE_DOMAIN_GENE,
        author_name='Charles Tapley Hoyt',
        citation_name='EC',
        namespace_query_url='https://enzyme.expasy.org/EC/[VALUE]',
        values=values,
        functions='P',
        file=file
    )


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
        self.id_prosite = {}
        self.id_uniprot = {}

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
        enzyme = self.id_enzyme.get(expasy_id)

        if enzyme is not None:
            self.session.add(enzyme)
            return enzyme

        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            enzyme = self.id_enzyme[expasy_id] = Enzyme(
                expasy_id=expasy_id,
                description=description
            )
            self.session.add(enzyme)

        return enzyme

    def get_or_create_prosite(self, prosite_id, **kwargs):
        """

        :param str prosite_id:
        :param kwargs:
        :rtype: Prosite
        """
        prosite = self.id_prosite.get(prosite_id)

        if prosite is not None:
            self.session.add(prosite)
            return prosite

        prosite = self.get_prosite_by_id(prosite_id)

        if prosite is None:
            prosite = self.id_prosite[prosite_id] = Prosite(prosite_id=prosite_id, **kwargs)
            self.session.add(prosite)

        return prosite

    def get_or_create_protein(self, accession_number, entry_name, **kwargs):
        """

        :param accession_number:
        :param entry_name:
        :param kwargs:
        :rtype: Protein
        """
        protein = self.id_uniprot.get(accession_number)

        if protein is not None:
            self.session.add(protein)
            return protein

        protein = self.get_protein_by_uniprot_id(uniprot_id=accession_number)

        if protein is None:
            protein = self.id_uniprot[accession_number] = Protein(
                accession_number=accession_number,
                entry_name=entry_name,
                **kwargs
            )
            self.session.add(protein)

        return protein

    def populate(self, tree_path=None, database_path=None):
        """Populates everything"""
        self.populate_tree(path=tree_path)
        self.populate_database(path=database_path)

    def populate_tree(self, path=None, force_download=False):
        """Downloads and populates the ExPASy tree

        :param Optional[str] path: A custom url to download
        :param bool force_download: If true, overwrites a previously cached file
        """
        tree = get_tree(path=path, force_download=force_download)

        for expasy_id, data in tqdm(tree.nodes_iter(data=True), desc='Classes', total=tree.number_of_nodes()):
            self.get_or_create_enzyme(
                expasy_id=expasy_id,
                description=data['description']
            )

        for parent_id, child_id in tqdm(tree.edges_iter(), desc='Tree', total=tree.number_of_edges()):
            parent = self.id_enzyme[parent_id]
            child = self.id_enzyme[child_id]
            parent.children.append(child)

        log.info("committing")
        self.session.commit()

    def populate_database(self, path=None, force_download=False):
        """Populates the ExPASy database.

        :param Optional[str] path: A custom url to download
        :param bool force_download: If true, overwrites a previously cached file
        """
        data_dict = get_expasy_database(path=path, force_download=force_download)

        for data in tqdm(data_dict, desc='Database'):
            if data['DELETED'] or data['TRANSFERRED']:
                continue  # if both are false then proceed

            expasy_id = data[ID]

            enzyme = self.get_or_create_enzyme(
                expasy_id=expasy_id,
                description=data[DE]
            )

            parent_id, _ = give_edge(data[ID])
            enzyme.parent = self.get_enzyme_by_id(parent_id)

            for prosite_id in data.get(PR, []):
                prosite = self.get_or_create_prosite(prosite_id)
                enzyme.prosites.append(prosite)

            for uniprot_data in data.get(DR, []):
                protein = self.get_or_create_protein(
                    accession_number=uniprot_data['accession_number'],
                    entry_name=uniprot_data['entry_name']
                )
                enzyme.proteins.append(protein)

        log.info("committing")
        self.session.commit()

    def get_enzyme_by_id(self, expasy_id):
        """Gets an enzyme by its ExPASy identifier.
        
        Implementation note: canonicalizes identifier to remove all spaces first.

        :param str expasy_id: An ExPASy identifier. Example: 1.3.3.- or 1.3.3.19
        :rtype: Optional[Enzyme]
        """
        canonical_expasy_id = normalize_expasy_id(expasy_id)
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

    def get_prosites_by_expasy_id(self, expasy_id):
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

    def enrich_proteins_with_enzyme_families(self, graph):
        """Enriches proteins in the BEL graph with IS_A relations to their enzyme classes.

        1. Gets a list of UniProt proteins
        2. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            namespace = data.get(NAMESPACE)

            if namespace is None:
                continue

            if namespace not in {'UP', 'UNIPROT'}:
                continue

            enzymes = self.get_enzymes_by_uniprot_id(data[IDENTIFIER])

            if enzymes is None:
                continue

            for enzyme in enzymes:
                graph.add_unqualified_edge(enzyme.serialize_to_bel(), node, IS_A)

    def enrich_enzymes(self, graph):
        """Add all children of entries (enzyme codes with 4 numbers in them that can be directly annotated to proteins)

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            namespace = data.get(NAMESPACE)

            if namespace is None:
                continue

            if namespace not in {'EXPASY', 'EC'}:
                continue

            parent = self.get_parent(data[NAME])
            if parent is not None:
                graph.add_unqualified_edge(parent.serialize_to_bel(), node, IS_A)

            children = self.get_children(data[NAME])
            if children is not None:
                for child in children:
                    graph.add_unqualified_edge(node, child.serialize_to_bel(), IS_A)

    def enrich_enzymes_with_prosites(self, graph):
        """Enriches Enzyme classes in the graph with ProSites.

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            namespace = data.get(NAMESPACE)

            if namespace is None:
                continue

            if namespace not in {'EXPASY', 'EC'}:
                continue

            prosites = self.get_prosites_by_expasy_id(data[NAME])
            if prosites is not None:
                for prosite in prosites:
                    graph.add_unqualified_edge(node, prosite.serialize_to_bel(), IS_A)

    def write_bel_namespace(self, file):
        values = [expasy_id for expasy_id, in self.session.query(Enzyme.expasy_id).all()]
        _write_bel_namespace_helper(values, file)

    def deploy_bel_namespace(self):
        """Creates and deploys the Gene Names Namespace

        :rtype: Optional[str]
        """
        file_name = get_today_arty_namespace('ec')

        with open(file_name, 'w') as file:
            self.write_bel_namespace(file)

        return deploy_namespace(file_name, module_name='ec')
