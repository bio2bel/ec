# -*- coding: utf-8 -*-

"""Manager for Bio2BEL ExPASy."""

import logging
from typing import List, Mapping, Optional

from tqdm import tqdm

from bio2bel import AbstractManager
from bio2bel.manager.flask_manager import FlaskMixin
from bio2bel.manager.namespace_manager import BELNamespaceManagerMixin
from pybel import BELGraph
from pybel.constants import IS_A, NAME, NAMESPACE
from pybel.dsl import BaseEntity
from pybel.manager.models import Namespace, NamespaceEntry
from .constants import MODULE_NAME
from .models import Base, Enzyme, Prosite, Protein, enzyme_prosite, enzyme_protein
from .parser.database import get_expasy_database, ID, DE, PR, DR
from .parser.tree import get_tree, give_edge, normalize_expasy_id

__all__ = ['Manager']

log = logging.getLogger(__name__)


class Manager(AbstractManager, BELNamespaceManagerMixin, FlaskMixin):
    """Creates a connection to database and a persistent session using SQLAlchemy."""

    _base = Base
    module_name = MODULE_NAME
    flask_admin_models = [Enzyme, Protein, Prosite]

    namespace_model = Enzyme
    has_names = False
    identifiers_recommended = 'Enzyme Nomenclature'
    identifiers_pattern = r'^\d+\.-\.-\.-|\d+\.\d+\.-\.-|\d+\.\d+\.\d+\.-|\d+\.\d+\.\d+\.(n)?\d+$'
    identifiers_miriam = 'MIR:00000004'
    identifiers_namespace = 'ec-code'
    identifiers_url = 'http://identifiers.org/ec-code/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #: Maps canonicalized ExPASy enzyme identifiers to their SQLAlchemy models
        self.id_enzyme = {}
        self.id_prosite = {}
        self.id_uniprot = {}

    def is_populated(self) -> bool:
        """Check if the database is already populated."""
        return 0 < self.count_enzymes()

    def count_enzymes(self) -> int:
        """Count the number of enzyme entries in the database."""
        return self._count_model(Enzyme)

    def count_enzyme_prosites(self) -> int:
        """Count the number of enzyme-prosite annotations."""
        return self._count_model(enzyme_prosite)

    def count_prosites(self) -> int:
        """Count the number of ProSite entries in the database."""
        return self._count_model(Prosite)

    def count_enzyme_proteins(self) -> int:
        """Count the number of enzyme-protein annotations."""
        return self._count_model(enzyme_protein)

    def count_proteins(self) -> int:
        """Count the number of protein entries in the database."""
        return self._count_model(Protein)

    def summarize(self) -> Mapping[str, int]:
        """Return a summary dictionary over the content of the database. """
        return dict(
            enzymes=self.count_enzymes(),
            enzyme_prosites=self.count_enzyme_prosites(),
            prosites=self.count_prosites(),
            enzyme_proteins=self.count_enzyme_proteins(),
            proteins=self.count_proteins()
        )

    def get_or_create_enzyme(self, expasy_id: str, description: Optional[str] = None) -> Enzyme:
        """Get an enzyme from the database or creates it."""
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

    def get_or_create_prosite(self, prosite_id: str, **kwargs) -> Prosite:
        """Get a prosite from the database or creates it."""
        prosite = self.id_prosite.get(prosite_id)

        if prosite is not None:
            self.session.add(prosite)
            return prosite

        prosite = self.get_prosite_by_id(prosite_id)

        if prosite is None:
            prosite = self.id_prosite[prosite_id] = Prosite(prosite_id=prosite_id, **kwargs)
            self.session.add(prosite)

        return prosite

    def get_or_create_protein(self, accession_number: str, entry_name: str, **kwargs) -> Protein:
        """Get a protein by its UniProt accession or create it.

        :param accession_number:
        :param entry_name:
        :param kwargs:
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

    def populate(self, tree_path: Optional[str] = None, database_path: Optional[str] = None) -> None:
        """Populate the database..

        :param tree_path:
        :param database_path:
        """
        self.populate_tree(path=tree_path)
        self.populate_database(path=database_path)

    def populate_tree(self, path: Optional[str] = None, force_download: bool = False) -> None:
        """Download and populate the ExPASy tree.

        :param path: A custom url to download
        :param force_download: If true, overwrites a previously cached file
        """
        tree = get_tree(path=path, force_download=force_download)

        for expasy_id, data in tqdm(tree.nodes(data=True), desc='Classes', total=tree.number_of_nodes()):
            self.get_or_create_enzyme(
                expasy_id=expasy_id,
                description=data['description']
            )

        for parent_id, child_id in tqdm(tree.edges(), desc='Tree', total=tree.number_of_edges()):
            parent = self.id_enzyme[parent_id]
            child = self.id_enzyme[child_id]
            parent.children.append(child)

        log.info("committing")
        self.session.commit()

    def populate_database(self, path: Optional[str] = None, force_download: bool = False) -> None:
        """Populate the ExPASy database.

        :param path: A custom url to download
        :param force_download: If true, overwrites a previously cached file
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

    def get_enzyme_by_id(self, expasy_id: str) -> Optional[Enzyme]:
        """Get an enzyme by its ExPASy identifier.

        Implementation note: canonicalizes identifier to remove all spaces first.

        :param expasy_id: An ExPASy identifier. Example: 1.3.3.- or 1.3.3.19
        """
        canonical_expasy_id = normalize_expasy_id(expasy_id)
        return self.session.query(Enzyme).filter(Enzyme.expasy_id == canonical_expasy_id).one_or_none()

    def get_parent_by_expasy_id(self, expasy_id: str) -> Optional[Enzyme]:
        """Return the parent ID of ExPASy identifier if exist otherwise returns None.

        :param expasy_id: An ExPASy identifier
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.parent

    def get_children_by_expasy_id(self, expasy_id: str) -> Optional[List[Enzyme]]:
        """Return a list of enzymes which are children of the enzyme with the given ExPASy enzyme identifier.

        :param expasy_id: An ExPASy enzyme identifier
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.children

    def get_protein_by_uniprot_id(self, uniprot_id: str) -> Optional[Protein]:
        """Get a protein having the given UniProt identifier.

        :param uniprot_id: A UniProt identifier

        >>> from bio2bel_expasy import Manager
        >>> manager = Manager()
        >>> protein = manager.get_protein_by_uniprot_id('Q6AZW2')
        >>> protein.accession_number
        'Q6AZW2'
        """
        return self.session.query(Protein).filter(Protein.accession_number == uniprot_id).one_or_none()

    def get_prosite_by_id(self, prosite_id: str) -> Optional[Prosite]:
        """Get a ProSite having the given ProSite identifier.

        :param prosite_id: A ProSite identifier
        """
        return self.session.query(Prosite).filter(Prosite.prosite_id == prosite_id).one_or_none()

    def get_prosites_by_expasy_id(self, expasy_id: str) -> Optional[List[Prosite]]:
        """Get a list of ProSites associated with the enzyme corresponding to the given identifier.

        :param expasy_id: An ExPASy identifier
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.prosites

    def get_enzymes_by_prosite_id(self, prosite_id: str) -> Optional[List[Enzyme]]:
        """Return a list of enzymes associated with the given ProSite ID.

        :param prosite_id: ProSite identifier
        """
        prosite = self.get_prosite_by_id(prosite_id)

        if prosite is None:
            return

        return prosite.enzymes

    def get_proteins_by_expasy_id(self, expasy_id: str) -> Optional[List[Protein]]:
        """Return a list of UniProt entries as tuples (accession_number, entry_name) of the given enzyme_id.

        :param expasy_id: An ExPASy identifier
        """
        enzyme = self.get_enzyme_by_id(expasy_id)

        if enzyme is None:
            return

        return enzyme.proteins

    def get_enzymes_by_uniprot_id(self, uniprot_id: str) -> Optional[List[Enzyme]]:
        """Return a list of enzymes annotated to the protein with the given UniProt accession number.

        :param uniprot_id: A UniProt identifier

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

    def enrich_proteins_with_enzyme_families(self, graph: BELGraph) -> None:
        """Enrich proteins in the BEL graph with IS_A relations to their enzyme classes.

        1. Gets a list of UniProt proteins
        2. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds

        """
        for node in list(graph):
            namespace = node.get(NAMESPACE)

            if namespace is None:
                continue

            if namespace.lower() not in {'up', 'uniprot'}:
                continue

            enzymes = self.get_enzymes_by_uniprot_id(node.identifier)

            if enzymes is None:
                continue

            for enzyme in enzymes:
                graph.add_unqualified_edge(enzyme.as_bel(), node, IS_A)

    def look_up_enzyme(self, node: BaseEntity) -> Optional[Enzyme]:
        """Try to get an enzyme model from the given node."""
        namespace = node.get(NAMESPACE)
        if namespace is None:
            return

        if namespace.lower() not in {'expasy', 'ec', 'eccode'}:
            return

        name = node.get(NAME)

        return self.get_enzyme_by_id(name)

    def enrich_enzyme_with_proteins(self, graph: BELGraph, node: BaseEntity) -> None:
        """Enrich an enzyme with all of its member proteins."""
        enzyme = self.look_up_enzyme(node)
        if enzyme is None:
            return

        if enzyme.level == 4:
            for protein in enzyme.proteins:
                graph.add_is_a(protein.as_bel(), node)

    def enrich_enzyme_parents(self, graph: BELGraph, node: BaseEntity) -> None:
        """Enrich an enzyme with its parents."""
        enzyme = self.look_up_enzyme(node)
        if enzyme is None:
            return

        parent = enzyme.parent
        if parent is None:
            return
        graph.add_is_a(node, parent.as_bel())

        grandparent = parent.parent
        if grandparent is None:
            return
        graph.add_is_a(parent.as_bel(), grandparent.as_bel())

        greatgrandparent = grandparent.parent
        if greatgrandparent is None:
            return
        graph.add_is_a(grandparent.as_bel(), greatgrandparent.as_bel())

    def _enrich_enzyme_children_helper(self, graph: BELGraph, enzyme: Enzyme) -> None:
        for child in enzyme.children:
            child_bel = child.as_bel()
            graph.add_is_a(child_bel, enzyme.as_bel())
            self.enrich_enzyme_children(graph, child_bel)

    def enrich_enzyme_children(self, graph: BELGraph, node: BaseEntity) -> None:
        """Enrich an enzyme with all of its children."""
        enzyme = self.look_up_enzyme(node)
        if enzyme is None:
            return
        self._enrich_enzyme_children_helper(graph, enzyme)

    def enrich_enzymes(self, graph: BELGraph) -> None:
        """Add all children of entries."""
        for node in list(graph):
            self.enrich_enzyme_parents(graph, node)
            self.enrich_enzyme_children(graph, node)
            self.enrich_enzyme_with_proteins(graph, node)

    def enrich_enzymes_with_prosites(self, graph: BELGraph) -> None:
        """Enrich enzyme classes in the graph with ProSites."""
        for node in list(graph):
            enzyme = self.look_up_enzyme(node)
            if enzyme is None:
                continue

            for prosite in enzyme.prosites:
                graph.add_is_a(node, prosite.as_bel())

    def _add_admin(self, app, **kwargs):
        """Add a Flask Admin interface to an application.

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

    @staticmethod
    def _get_identifier(model: Enzyme) -> str:
        return model.expasy_id

    def _create_namespace_entry_from_model(self, model: Enzyme, namespace: Namespace) -> NamespaceEntry:
        return NamespaceEntry(
            namespace=namespace,
            name=model.expasy_id,
            identifier=model.expasy_id,
            encoding='GRP',
        )
