# -*- coding: utf-8 -*-

import logging

from pybel.constants import FUNCTION, IS_A, NAME, NAMESPACE, PROTEIN
from pybel_tools import pipeline
from .constants import EXPASY
from .manager import Manager

log = logging.getLogger(__name__)

__all__ = [
    'enrich_enzyme_classes',
]


def _check_namespaces(data, bel_function, bel_namespace):
    """Makes code more structured and reusable."""
    if data[FUNCTION] != bel_function:
        return False

    if NAMESPACE not in data:
        return False

    if data[NAMESPACE] == bel_namespace:
        return True

    elif data[NAMESPACE] != bel_namespace:
        log.warning("Unable to map namespace: %s", data[NAMESPACE])
        return False


def node_is_protein(graph, node):
    """True if node is protein, False if else.

    :param graph: BELGraph
    :param node: tuple node
    :return: bool
    """
    return PROTEIN == graph.node[node][FUNCTION]


@pipeline.in_place_mutator
def enrich_enzyme_classes(graph, connection=None):
    """Enriches Enzyme Classes for proteins in the graph

    1. Gets a list of proteins
    2. get UniProtKB entries
    3. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds
    4. Ensures all parent enzyme classes for those enzyme classes

    :param pybel.BELGraph graph: A BEL graph
    :param connection: connection string or manager
    :rtype: pybel.BELGraph
    """
    m = Manager.ensure(connection)
    graph = enrich_parents_classes(graph=graph)
    graph = enrich_children_classes(graph=graph)

    for node, data in graph.nodes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        uniprot_list = m.get_uniprot(data[NAME])

        if not uniprot_list:
            log.warning("enrich_enzyme_classes():Unable to find node: %s", node)
            continue
        for prot in uniprot_list:
            protein_tuple = graph.add_node_from_data(prot.serialize_to_bel())
            graph.add_unqualified_edge(node, protein_tuple, IS_A)

    return graph


@pipeline.in_place_mutator
def enrich_prosite_classes(graph, connection=None):
    """enriches Enzyme classes for prosite in the graph

    :param pybel.BELGraph graph:
    :param connection:
    :rtype pybel.BELGraph
    """
    m = Manager.ensure(connection=connection)
    graph = enrich_parents_classes(graph=graph)
    graph = enrich_children_classes(graph=graph)

    for node, data in graph.nodes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        prosite_list = m.get_prosite(data[NAME])
        if not prosite_list:
            log.warning('enrich_prosite_classes():Unable to find node %s', node)
            continue
        for prosite in prosite_list:
            prosite_tuple = graph.add_node_from_data(prosite.serialize_to_bel())
            graph.add_unqualified_edge(node, prosite_tuple, IS_A)

    return graph


@pipeline.in_place_mutator
def enrich_parents_classes(graph, connection=None):
    """Enriches graph nodes with parents.

    :param pybel.BELGraph graph:
    :param connection:
    :rtype pybel.BELGraph
    """
    m = Manager.ensure(connection=connection)

    for node, data in graph.nodes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        parent = m.get_parent(data[NAME])
        if not parent:
            log.warning('enrich_parents_classes(): Unable to find node %s', data[NAME])
            continue

        while parent:
            parent_tuple = graph.add_node_from_data(parent.serialize_to_bel())
            graph.add_unqualified_edge(node, parent_tuple, IS_A)
            parent = m.get_parent(parent_tuple[2])

    return graph


@pipeline.in_place_mutator
def enrich_children_classes(graph, connection=None):
    """Enriches graph nodes with children.

    :param pybel.BELGraph graph:
    :param connection:
    :rtype pybel.BELGraph
    """
    m = Manager.ensure(connection=connection)

    for node, data in graph.nodes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        children = m.get_children(data[NAME])
        if not children:
            log.warning("enrich_children_classes(): Unable to find node %s", data[NAME])
            continue

        for child in children:
            children_tuple = graph.add_node_from_data(child.serialize_to_bel())
            graph.add_unqualified_edge(node, children_tuple, IS_A)

    return graph
