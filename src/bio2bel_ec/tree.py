# -*- coding: utf-8 -*-

from urllib.request import urlretrieve

import networkx as nx
from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import CONFIDENCE

from .constants import ENZCLASS_URL, ENZCLASS_FILE

__all__ = [
    'populate_tree',
    'write_expasy_tree',
]


def download_res():
    urlretrieve(ENZCLASS_URL, ENZCLASS_FILE)


def populate_tree(fileName=ENZCLASS_FILE):
    """Populates graph from a given specific file.

    :param fileName str
    :return networkx.DiGraph
    """

    graph = nx.DiGraph()

    def give_edge(head_str):
        nums = head_str.split('.')
        for i, obj in enumerate(nums):
            nums[i] = obj.strip()

        while '-' in nums:
            nums.remove('-')

        if len(nums) == 1:
            return None
        elif len(nums) == 2:
            return ("{}. -. -.-".format(nums[0]), "{}.{:>2}. -.-".format(nums[0], nums[1]))
        elif len(nums) == 3:
            return ("{}.{:>2}. -.-".format(nums[0], nums[1]), "{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2]))
        elif len(nums) == 4:
            return ("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2]),
                    "{}.{:>2}.{:>2}.{}".format(nums[0], nums[1], nums[2], nums[3]))

    with open(str(fileName), 'r') as file:
        for line in file:
            line.rstrip('\n')
            if not line[0].isnumeric():
                continue
            head = line[:10]
            e = give_edge(head)
            if e is not None:
                graph.add_edge(*e)

    return graph


def write_expasy_tree_boilerplate(file=None):
    """Writes the BEL document header to the file

    :param file file: A writeable file or file like. Defaults to stdout
    """
    write_boilerplate(
        document_name='Expasy Enzyme Tree',
        authors='Aram Grigoryan and Charles Tapley Hoyt',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents relations from EXPASY ENZYME nomenclature database""",
        namespace_dict={
            'EC': '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*',
        },
        namespace_patterns={},
        annotations_dict={'Confidence': CONFIDENCE},
        annotations_patterns={},
        file=file
    )


def write_expasy_tree_body(graph, file):
    """Creates the lines of BEL document that represents the Expasy Enzyme tree

    :param networkx.DiGraph graph: A graph representing the Expasy tree from :func:`main`
    :param file file: A writeable file or file-like. Defaults to stdout.
    """
    print('SET Citation = {"PubMed","Expasy","12824418"}', file=file)
    print('SET Evidence = "Expasy Definitions"', file=file)
    print('SET Confidence = "Axiomatic"', file=file)

    for parent, child in graph.edges_iter():
        print(
            'p(EC:{}) isA p(EC:{})'.format(
                ensure_quotes(child),
                ensure_quotes(parent),
            ),
            file=file
        )

    print('UNSET ALL', file=file)


def write_expasy_tree(file=None):
    """Creates the entire BEL document representing the Expasy tree

    :param file file: A writeable file or file-like. Defaults to stdout.
    """
    graph = populate_tree()
    write_expasy_tree_boilerplate(file)
    write_expasy_tree_body(graph, file)
