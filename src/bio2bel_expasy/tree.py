# -*- coding: utf-8 -*-

import os
import re
from urllib.request import urlretrieve

import networkx as nx
from pybel.resources.arty import get_latest_arty_namespace
from pybel.resources.defaults import CONFIDENCE
from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate

from .constants import EC_DATA_FILE_REGEX, ENZCLASS_DATA_FILE, ENZCLASS_DATA_URL, ENZCLASS_FILE, ENZCLASS_URL

__all__ = [
    'populate_tree',
    'write_expasy_tree',
    'standard_ec_id',
    'give_edge',
    'edge_description'
]


def download_res(path=None, force_download=False):
    """Download database resources if not found

    :param Optional[str] path: The destination of the download
    :param Optional[bool] force_download: True to force download
    """
    if not os.path.exists(ENZCLASS_FILE) or force_download:
        urlretrieve(ENZCLASS_URL, path or ENZCLASS_FILE)


def download_ec_data(force_download=False):
    """Downloads the file

    :param force_download: bool to force download
    """
    if not os.path.exists(ENZCLASS_DATA_FILE) or force_download:
        urlretrieve(ENZCLASS_DATA_URL, ENZCLASS_DATA_FILE)


def standard_ec_id(non_standard_ec_id):
    """Rerturns standardized expasy id string

    :param str non_standard_ec_id: str
    :return str:
    """
    return non_standard_ec_id.replace(" ", "")


def non_standard_ec_id(standard_ec_id):
    """Returns non canonical way of given expasy_id found in hierarchy data file.

    :param standard_ec_id:
    :return: str
    """
    nums = standard_ec_id.split('.')
    non_standard_ec_id = ''
    for obj in nums:
        if obj.isdigit():
            if int(obj) > 9:
                non_standard_ec_id += obj
                non_standard_ec_id += '.'
            else:
                non_standard_ec_id += ' '
                non_standard_ec_id += obj
                non_standard_ec_id += '.'
        else:
            non_standard_ec_id += ' '
            non_standard_ec_id += obj
            non_standard_ec_id += '.'

    k = non_standard_ec_id.rfind(' ')
    non_standard_ec_id = non_standard_ec_id[:k] + non_standard_ec_id[k + 1:]
    return non_standard_ec_id.strip().strip('.')


def give_edge(head_str):
    """Returns (parent, child) tuple for given id

    :param head_str:
    :return: tuple
    """
    head_str = standard_ec_id(head_str)
    nums = head_str.split('.')
    for i, obj in enumerate(nums):
        nums[i] = obj.strip()

    while '-' in nums:
        nums.remove('-')

    if len(nums) == 1:
        return None, None
    elif len(nums) == 2:
        return (standard_ec_id("{}. -. -.-".format(nums[0])),
                standard_ec_id("{}.{:>2}. -.-".format(nums[0], nums[1])))
    elif len(nums) == 3:
        return (standard_ec_id("{}.{:>2}. -.-".format(nums[0], nums[1])),
                standard_ec_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])))
    elif len(nums) == 4:
        return (standard_ec_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])),
                standard_ec_id("{}.{:>2}.{:>2}.{}".format(nums[0], nums[1], nums[2], nums[3])))


def edge_description(expasy_id, file=None):
    expasy_id = non_standard_ec_id(expasy_id)
    file = open(ENZCLASS_FILE, 'r') if file is None else file
    for line in file:
        if expasy_id in line:
            return line.split('-  ')[1].strip().strip('.')
    return None


def populate_tree(path_enzclass=ENZCLASS_FILE, path_enzclass_data=ENZCLASS_DATA_FILE, force_download=False):
    """Populates graph from a given specific file.

    :param Optional[str] path_enzclass: Path to
    :return networkx.DiGraph
    """
    download_res(force_download=force_download)

    graph = nx.DiGraph()

    with open(path_enzclass, 'r') as file:
        for line in file:
            line.rstrip('\n')
            if not line[0].isnumeric():
                continue
            head = line[:10]
            parent, child = give_edge(head)
            name = line[11:]
            name = name.strip().strip('.')
            if parent is not None:
                graph.add_node(child, name=name)
                graph.add_edge(parent, child)

    def get_full_list_of_ec_ids(force_download=False):
        """Apparantly Returns the full list of EC entries
        :return lst: lst
        """

        download_ec_data(force_download=force_download)
        with open(path_enzclass_data, 'r') as ec_file:
            e_read = ec_file.read()

            matches = re.finditer(EC_DATA_FILE_REGEX, e_read)
            new_list = []

            for regex_obj in matches:
                new_list.append(regex_obj.group().split('   ')[1])

            return new_list

    id_list = get_full_list_of_ec_ids(force_download=force_download)
    for node in id_list:
        parent, child = give_edge(node)
        if parent is not None:
            graph.add_edge(parent, child)
    return graph


def write_expasy_tree_boilerplate(file=None):
    """Writes the BEL document header to the file

    :param file file: A writeable file or file like. Defaults to stdout
    """
    write_boilerplate(
        name='Expasy Enzyme Tree',
        authors='Aram Grigoryan and Charles Tapley Hoyt',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents relations from EXPASY ENZYME nomenclature database""",
        namespace_url={'EC': get_latest_arty_namespace('enzyme-class')},
        namespace_patterns={
            # 'EC': '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*',
        },
        annotation_url={'Confidence': CONFIDENCE},
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
