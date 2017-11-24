# -*- coding: utf-8 -*-

import logging

from pybel.constants import FUNCTION, PROTEIN, NAMESPACE, NAME, IS_A
from pybel.struct.filters import filter_nodes
from pybel_tools import pipeline

from .database import Manager

EXPASY = 'expasy'

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


def annotate_parents(graph, node):
    """Annotates the set of possibly multiple Enzyme Class parents to the node in the graph

    :param BELGraph graph: A BEL graph
    :param tuple node: A PyBEL node tuple
    """
    # parent_node = (node[0], node[1], get_parent(node[2]))
    # graph.add_edge(parent_node, node)
    raise NotImplementedError


def annotate_all_parents(graph):
    """Adds the set of possibly multiple Enzyme Class memberships for all nodes in a graph

    :param BELGraph graph: A BEL graph
    """
    raise NotImplementedError

    # nodes = list(filter_nodes(graph, node_is_protein))
    # print(len(nodes))
    #
    # for node in nodes:
    #     annotate_parents(graph, node)


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

    for node, data in graph.nodes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        uniprot_list = m.get_uniprot(data[NAME])

        if not uniprot_list:
            log.warning("Unable to find node: %s", node)
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

    for node, data in graph.noes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        prosite_list = m.get_prosite(data[NAME])
        if not prosite_list:
            log.warning('Unable to find node %s', node)
            continue
        for prosite in prosite_list:
            prosite_tuple = graph.add_node_from_data(prosite.serialize_to_bel())
            graph.add_unqualified_edge(node, prosite_tuple, IS_A)

    return graph


@pipeline.in_place_mutator
def enrich_parents_classes(graph, connection=None):
    """

    :param pybel.BELGraph graph:
    :param connection:
    :rtype pybel.BELGraph
    """
    m = Manager.ensure()

    for node, data in graph.nodes(data=True):
        if not _check_namespaces(data, PROTEIN, EXPASY):
            continue
        parents_list = m.get_parent()
        if not parents_list:
            log.warning('Unable to find node %s', node)
            continue
        for parent in parents_list:
            parent_tuple = graph.add_node_from_data(parent.serialize_to_bel())
            graph.add_unqualified_edge(node, parent_tuple, IS_A)

    return graph