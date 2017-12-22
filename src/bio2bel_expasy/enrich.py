# -*- coding: utf-8 -*-

import logging

from pybel.constants import IS_A, NAME, PROTEIN
from .constants import EXPASY
from .manager import Manager
from .utils import check_namespaces

log = logging.getLogger(__name__)

__all__ = [
    'enrich_proteins',
    'enrich_prosite_classes',
]


def enrich_proteins(graph, connection=None):
    """Enriches proteins in the BEL graph with IS_A relations to their enzyme classes.

    1. Gets a list of UniProt proteins
    2. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_expasy.Manager
    """
    m = Manager.ensure(connection)
    m.enrich_proteins(graph)


def enrich_prosite_classes(graph, connection=None):
    """enriches Enzyme classes for ProSite in the graph.

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_expasy.Manager
    """
    m = Manager.ensure(connection=connection)
    m.enrich_prosite_classes(graph)


def enrich_parents_classes(graph, connection=None):
    """Enriches graph nodes with parents.

    :param pybel.BELGraph graph: A BEL graph
    :param connection:
    """
    m = Manager.ensure(connection=connection)

    for node, data in graph.nodes(data=True):
        if not check_namespaces(data, PROTEIN, EXPASY):
            continue
        parent = m.get_parent(data[NAME])
        if not parent:
            log.warning('enrich_parents_classes(): Unable to find node %s', data[NAME])
            continue

        while parent:
            parent_tuple = graph.add_node_from_data(parent.serialize_to_bel())
            graph.add_unqualified_edge(node, parent_tuple, IS_A)
            parent = m.get_parent(parent_tuple[2])


def enrich_children_classes(graph, connection=None):
    """Enriches graph nodes with children.

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_expasy.Manager
    """
    m = Manager.ensure(connection=connection)

    for node, data in graph.nodes(data=True):
        if not check_namespaces(data, PROTEIN, EXPASY):
            continue
        children = m.get_children(data[NAME])
        if not children:
            log.warning("enrich_children_classes(): Unable to find node %s", data[NAME])
            continue

        for child in children:
            children_tuple = graph.add_node_from_data(child.serialize_to_bel())
            graph.add_unqualified_edge(node, children_tuple, IS_A)
