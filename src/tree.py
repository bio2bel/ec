# -*- coding: utf-8 -*-

import os
from urllib.request import urlretrieve

import networkx as nx
from pybel.constants import PYBEL_DATA_DIR

ENZCLASS_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzclass.txt'

ENZCLASS_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'expasy')
if not os.path.exists(ENZCLASS_DATA_DIR):
    os.makedirs(ENZCLASS_DATA_DIR)

ENZCLASS_FILE = os.path.join(ENZCLASS_DATA_DIR, 'enzclass.txt')


def download_res():
    urlretrieve(ENZCLASS_URL, ENZCLASS_FILE)


if not os.path.isfile(ENZCLASS_FILE):
    download_res()


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

        return nums

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


if __name__ == '__main__':
    g = populate_tree()
    print(g.edges())
    pass
