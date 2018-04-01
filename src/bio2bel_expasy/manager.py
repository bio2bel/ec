# -*- coding: utf-8 -*-

import logging

from tqdm import tqdm

from bio2bel import AbstractManager
from pybel.constants import IDENTIFIER, IS_A, NAME, NAMESPACE, NAMESPACE_DOMAIN_GENE
from pybel.resources import write_namespace
from pybel.resources.arty import get_today_arty_namespace
from pybel.resources.deploy import deploy_namespace
from .constants import MODULE_NAME
from .models import Base, Enzyme, Prosite, Protein, enzyme_prosite, enzyme_protein
from .parser.database import *
from .parser.tree import get_tree, give_edge, normalize_expasy_id

__all__ = ['Manager']

log = logging.getLogger(__name__)


def _write_bel_namespace_helper(values, file):
    """
    :param iter[str] or dict[str,str] values:
    :param file:
    """
    write_namespace(
        namespace_name='ExPASy Enzyme Classes',
        namespace_keyword='EC',
        namespace_domain=NAMESPACE_DOMAIN_GENE,
        author_name='Charles Tapley Hoyt',
        citation_name='EC',
        namespace_query_url='https://enzyme.expasy.org/EC/[VALUE]',
        values=values,
        functions='P',
        file=file
    )


class Manager(AbstractManager):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    module_name = MODULE_NAME
    flask_admin_models = [Enzyme, Protein, Prosite]

    def __init__(self, connection=None):
        """
        :param str connection: SQLAlchemy
        """
        super().__init__(connection=connection)

        #: Maps canonicalized ExPASy enzyme identifiers to their SQLAlchemy models
        self.id_enzyme = {}
        self.id_prosite = {}
        self.id_uniprot = {}

    @property
    def base(self):
        return Base

    def count_enzymes(self):
        """Counts the number of enzyme entries in the database

        :rtype: int
        """
        return self._count_model(Enzyme)

    def count_enzyme_prosites(self):
        """Counts the number of enzyme-prosite annotations

        :rtype: int
        """
        return self._count_model(enzyme_prosite)

    def count_prosites(self):
        """Counts the number of ProSite entries in the database

        :rtype: int
        """
        return self._count_model(Prosite)

    def count_enzyme_proteins(self):
        """Counts the number of enzyme-protein annotations

        :rtype: int
        """
        return self._count_model(enzyme_protein)

    def count_proteins(self):
        """Counts the number of protein entries in the database

        :rtype: int
        """
        return self._count_model(Protein)

    def summarize(self):
        """Returns a summary dictionary over the content of the database

        :rtype: dict[str,int]
        """
        return dict(
            enzymes=self.count_enzymes(),
            enzyme_prosites=self.count_enzyme_prosites(),
            prosites=self.count_prosites(),
            enzyme_proteins=self.count_enzyme_proteins(),
            proteins=self.count_proteins()
        )

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
        """Populates everything

        :param Optional[str] tree_path:
        :param Optional[str] database_path:
        """
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

    def get_parent_by_expasy_id(self, expasy_id):
        """Returns the parent ID of ExPASy identifier if exist otherwise returns None

        :param str expasy_id: An ExPASy identifier
        :rtype: Optional[Enzyme]
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.parent

    def get_children_by_expasy_id(self, expasy_id):
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

    def _look_up_enzyme(self, data):
        """

        :param data:
        :return: Optional[Enzyme]
        """
        namespace = data.get(NAMESPACE)

        if namespace is None:
            return

        if namespace not in {'EXPASY', 'EC'}:
            return

        name = data.get(NAME)

        return self.get_enzyme_by_id(name)

    def enrich_enzyme_with_proteins(self, graph, node):
        """Enrich an enzyme with all of its member proteins

        :param pybel.BELGraph graph:
        :param tuple node:
        """
        data = graph.node[node]
        enzyme = self._look_up_enzyme(data)
        if enzyme is None:
            return

        if enzyme.level == 4:
            for protein in enzyme.proteins:
                graph.add_is_a(protein.serialize_to_bel(), node)

    def enrich_enzyme_parents(self, graph, node):
        """

        :param pybel.BELGraph graph:
        :param tuple node:
        """
        data = graph.node[node]
        enzyme = self._look_up_enzyme(data)
        if enzyme is None:
            return

        parent = enzyme.parent
        if parent is None:
            return
        graph.add_is_a(node, parent.serialize_to_bel())

        grandparent = parent.parent
        if grandparent is None:
            return
        graph.add_is_a(parent.serialize_to_bel(), grandparent.serialize_to_bel())

        greatgrandparent = grandparent.parent
        if greatgrandparent is None:
            return
        graph.add_is_a(grandparent.serialize_to_bel(), greatgrandparent.serialize_to_bel())

    def _enrich_enzyme_children_helper(self, graph, enzyme):
        """

        :param pybel.BELGraph graph:
        :param Enzyme enzyme:
        """
        for child in enzyme.children:
            child_bel = child.serialize_to_bel()
            graph.add_is_a(child_bel, enzyme.serialize_to_bel())
            self.enrich_enzyme_children(graph, child_bel.as_tuple())

    def enrich_enzyme_children(self, graph, node):
        """

        :param pybel.BELGraph graph:
        :param tuple node:
        """
        data = graph.node[node]
        enzyme = self._look_up_enzyme(data)
        if enzyme is None:
            return
        self._enrich_enzyme_children_helper(graph, enzyme)

    def enrich_enzymes(self, graph):
        """Add all children of entries (enzyme codes with 4 numbers in them that can be directly annotated to proteins)

        :param pybel.BELGraph graph: A BEL graph
        """
        for node in list(graph):
            self.enrich_enzyme_parents(graph, node)
            self.enrich_enzyme_children(graph, node)
            self.enrich_enzyme_with_proteins(graph, node)

    def enrich_enzymes_with_prosites(self, graph):
        """Enriches Enzyme classes in the graph with ProSites.

        :param pybel.BELGraph graph: A BEL graph
        """
        for node, data in graph.nodes(data=True):
            enzyme = self._look_up_enzyme(data)
            if enzyme is None:
                continue

            for prosite in enzyme.prosites:
                graph.add_is_a(node, prosite.serialize_to_bel())

    def write_bel_namespace(self, file):
        """

        :param file:
        :return:
        """
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

    def _add_admin(self, app, **kwargs):
        """Adds a Flask Admin interface to an application

        :param flask.Flask app:
        :param session:
        :param kwargs:
        :rtype: flask_admin.Admin
        """
        import flask_admin
        from flask_admin.contrib.sqla import ModelView

        admin = flask_admin.Admin(app, **kwargs)

        class EnzymeView(ModelView):
            column_hide_backrefs = False
            column_list = ('expasy_id', 'description', 'parents')

        admin.add_view(EnzymeView(Enzyme, self.session))
        admin.add_view(ModelView(Prosite, self.session))
        admin.add_view(ModelView(Protein, self.session))

        return admin
