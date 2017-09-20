# -*- coding: utf-8 -*-

import os
import re
from urllib.request import urlretrieve

from pybel.constants import PROTEIN, FUNCTION
from pybel.struct.filters import filter_nodes
from pybel_tools import pipeline

from bio2bel_ec.tree import populate_tree
from bio2bel_ec.constants import ENZCLASS_DATA_URL, ENZCLASS_DATA_FILE, EC_DATA_FILE_REGEX

__all__ = [
    'enrich_enzyme_classes',
]


def download_ec_data(force_download=False):
    """
    Downloads the file
    :return None:
    """
    if not os.path.exists(ENZCLASS_DATA_FILE) or force_download:
        urlretrieve(ENZCLASS_DATA_URL, ENZCLASS_DATA_FILE)


def get_parent(ec_str):
    """Get the parent enzyme string

    :param str ec_str: The child enzyme string
    :rtype str: str
    """

    def get_full_list_of_ec_ids(force_download=False):
        """
        Apparantly Returns the full list of EC entries
        :return lst: lst
        """
        download_ec_data()
        with open(ENZCLASS_DATA_FILE, 'r') as ec_file:
            e_read = ec_file.read()

            matches = re.finditer(EC_DATA_FILE_REGEX, e_read)
            new_list = []

            for regex_obj in matches:
                new_list.append(regex_obj.group().split('   ')[1])

            return new_list

    id_list = get_full_list_of_ec_ids()

    graph = populate_tree()
    if ec_str in id_list:
        ec_str = ec_str.split('.')
        ec_str[-1] = '-'
        ec_str = '.'.join(_ for _ in ec_str)
        return ec_str

    return graph.predecessors(ec_str)[-1]



    # raise NotImplementedError


def node_is_protein(graph, node):
    return PROTEIN == graph.node[node][FUNCTION]


def annotate_parents(graph, node):
    """Annotates the set of possibly multiple Enzyme Class parents to the node in the graph

    :param BELGraph graph: A BEL graph
    :param tuple node: A PyBEL node tuple
    """
    parent_node = (node[0], node[1], get_parent(node[2]))
    graph.add_edge(parent_node, node)


def annotate_all_parents(graph):
    """Adds the set of possibly multiple Enzyme Class memberships for all nodes in a graph

    :param BELGraph graph: A BEL graph
    """
    nodes = list(filter_nodes(graph, node_is_protein))
    print(len(nodes))

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
    annotate_all_parents(graph)
    for edge in graph.edges():
        print(edge)
    return graph
    #raise NotImplementedError
