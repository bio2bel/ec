# -*- coding: utf-8 -*-

from urllib.request import urlretrieve

import networkx as nx
import os
import re

from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import CONFIDENCE, get_latest_arty_namespace

from bio2bel_ec.constants import ENZCLASS_URL, ENZCLASS_FILE, ENZCLASS_DATA_FILE, ENZCLASS_DATA_URL, EC_DATA_FILE_REGEX

__all__ = [
    'populate_tree',
    'write_expasy_tree',
    'standard_ec_id',
]


def download_res(force=False):
    """

    :param force: bool to force download
    :return: None
    """
    if not os.path.exists(ENZCLASS_FILE) or force:
        urlretrieve(ENZCLASS_URL, ENZCLASS_FILE)

def download_ec_data(force_download=False):
    """
    Downloads the file
    :return None:
    """
    if not os.path.exists(ENZCLASS_DATA_FILE) or force_download:
        urlretrieve(ENZCLASS_DATA_URL, ENZCLASS_DATA_FILE)

def standard_ec_id(non_standard_ec_id):
    """
    Rerturns standardized ec id string
    :param str non_standard_ec_id: str
    :return str:
    """
    return non_standard_ec_id.replace(" ", "")


def populate_tree(fileName=ENZCLASS_FILE, force_download=False):
    """Populates graph from a given specific file.

    :param fileName str
    :return networkx.DiGraph
    """

    download_res()

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
            return (standard_ec_id("{}. -. -.-".format(nums[0])),
                    standard_ec_id("{}.{:>2}. -.-".format(nums[0], nums[1])))
        elif len(nums) == 3:
            return (standard_ec_id("{}.{:>2}. -.-".format(nums[0], nums[1])),
                    standard_ec_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])))
        elif len(nums) == 4:
            return (standard_ec_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])),
                    standard_ec_id("{}.{:>2}.{:>2}.{}".format(nums[0], nums[1], nums[2], nums[3])))

    with open(str(fileName), 'r') as file:
        for line in file:
            line.rstrip('\n')
            if not line[0].isnumeric():
                continue
            head = line[:10]
            e = give_edge(head)
            if e is not None:
                graph.add_edge(*e)

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

    id_list = get_full_list_of_ec_ids(force_download)
    for node in id_list:
        e = give_edge(node)
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
        namespace_dict={'EC': get_latest_arty_namespace('enzyme-class')},
        namespace_patterns={
            #'EC': '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*',
        },
        annotations_dict={'Confidence': CONFIDENCE},
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
