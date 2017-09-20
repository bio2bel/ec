# -*- coding: utf-8 -*-

import os
import re
from urllib.request import urlretrieve
import pyuniprot

from pybel.constants import PROTEIN, FUNCTION
from pybel.struct.filters import filter_nodes
from pybel_tools import pipeline

from bio2bel_ec.tree import populate_tree
from bio2bel_ec.constants import ENZCLASS_DATA_URL, ENZCLASS_DATA_FILE, EC_DATA_FILE_REGEX, SQL_DEFAULTS, SQLITE_DB_PATH

__all__ = [
    'enrich_enzyme_classes',
]



def mysql_connect(connection=SQL_DEFAULTS):
    """
    Sets a connection using MySQL
    :param str connection:
    :return None:
    """
    pyuniprot.set_mysql_connection(connection)

def sqlite_connect(db_path=SQLITE_DB_PATH):
    """
    Sets SQLite connection
    :param db_path: str
    :return: None
    """
    sqlite_db = os.path.join('sqlite:///', db_path)
    pyuniprot.set_connection(sqlite_db)

def connect(con_str=None, mysql=True):
    if mysql:
        mysql_connect() if con_str is None else mysql_connect(con_str)
    else:
        sqlite_connect() if con_str is None else sqlite_connect(con_str)

def get_parent(ec_str):
    """Get the parent enzyme string

    :param str ec_str: The child enzyme string
    :rtype str: str
    """
    graph = populate_tree()
    return graph.predecessors(ec_str)[-1]
    connect()

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
