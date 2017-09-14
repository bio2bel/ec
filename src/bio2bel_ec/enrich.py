# -*- coding: utf-8 -*-

from pybel.constants import PROTEIN, FUNCTION
from pybel.struct.filters import filter_nodes
from pybel_tools import pipeline

from bio2bel_ec.tree import populate_tree, download_res

__all__ = [
    'enrich_enzyme_classes',
]


def get_parent(ec_str):
    """Get the parent enzyme string

    :param str ec_str: The child enzyme string
    :rtype: str
    """
    graph = populate_tree()

    return graph.predecessors(ec_str)[-1]
    # raise NotImplementedError


def node_is_protein(graph, node):
    return PROTEIN == graph.node[node][FUNCTION]


def annotate_parents(graph, node):
    """Annotates the set of possibly multiple Enyzme Class parents to the node in the graph

    :param BELGraph graph: A BEL graph
    :param tuple node: A PyBEL node tuple
    """
    raise NotImplementedError


def annotate_all_parents(graph):
    """Adds the set of possibly multiple Enzyme Class memberships for all nodes in a graph

    :param BELGraph graph: A BEL graph
    """
    nodes = list(filter_nodes(graph, node_is_protein))

    for node in nodes:
        annotate_parents(graph, node)


@pipeline.mutator
def enrich_enzyme_classes(graph):
    """Enriches Enzyme Classes for proteins in the graph

    1. Gets a list of proteins
    2. looks up their entries with PyUniProt
    3. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds
    4. Ensures all parent enzyme classes for those enzyme classes

    :param pybel.BELGraph graph: A BEL graph
    """

    raise NotImplementedError


if __name__ == '__main__':
    download_res()
    ec_name = get_parent('1.14.99.-')
    print(ec_name)
