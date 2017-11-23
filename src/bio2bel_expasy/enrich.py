# -*- coding: utf-8 -*-

import logging

from pybel.constants import FUNCTION, PROTEIN, NAMESPACE
from pybel.struct.filters import filter_nodes
from pybel_tools import pipeline

from .database import Manager

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
    2. looks up their entries with PyUniProt
    3. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds
    4. Ensures all parent enzyme classes for those enzyme classes

    :param pybel.BELGraph graph: A BEL graph
    """
    m = Manager.ensure(connection)

    annotate_all_parents(graph)
    for edge in graph.edges():
        print(edge)

        # raise NotImplementedError
