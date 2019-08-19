# -*- coding: utf-8 -*-

import json
import logging
from typing import Optional

from bio2bel.downloading import make_downloader

from bio2bel_expasy.constants import EXPASY_TREE_DATA_PATH, EXPASY_TREE_URL
from bio2bel_expasy.utils import normalize_expasy_id

__all__ = [
    'normalize_expasy_id',
    'give_edge',
    'get_expasy_tree',
]

log = logging.getLogger(__name__)

download_expasy_tree = make_downloader(EXPASY_TREE_URL, EXPASY_TREE_DATA_PATH)


def give_edge(head_str):
    """Returns (parent, child) tuple for given id

    :param str head_str:
    :rtype: tuple
    """
    head_str = normalize_expasy_id(head_str)
    nums = head_str.split('.')
    for i, obj in enumerate(nums):
        nums[i] = obj.strip()

    while '-' in nums:
        nums.remove('-')

    level = len(nums)

    if level == 1:
        return level, None, "{}.-.-.-".format(nums[0])

    if level == 2:
        return (
            level,
            normalize_expasy_id("{}. -. -.-".format(nums[0])),
            normalize_expasy_id("{}.{:>2}. -.-".format(nums[0], nums[1])),
        )

    if level == 3:
        return (
            level,
            normalize_expasy_id("{}.{:>2}. -.-".format(nums[0], nums[1])),
            normalize_expasy_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])),
        )

    if level == 4:
        return (
            level,
            normalize_expasy_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])),
            normalize_expasy_id("{}.{:>2}.{:>2}.{}".format(nums[0], nums[1], nums[2], nums[3])),
        )


def _process_line(line, graph):
    line.rstrip('\n')
    if not line[0].isnumeric():
        return
    head = line[:10]
    l_nums, parent, child = give_edge(head)
    name = line[11:]
    name = name.strip().strip('.')
    graph.add_node(child, description=name)
    if parent is not None:
        graph.add_edge(parent, child)


def lines_to_json(lines):
    rv = {}
    for line in lines:
        if not line[0].isnumeric():
            continue
        head = line[:10]
        level, parent_expasy_id, expasy_id = give_edge(head)
        name = line[11:]
        name = name.strip().strip('.')

        rv[expasy_id] = {
            'concept': {
                'namespace': 'ec-code',
                'identifier': expasy_id,
            },
            'name': name,
            'level': level,
            'children': [],
        }
        if parent_expasy_id is not None:
            rv[expasy_id]['parent'] = {
                'namespace': 'ec-code',
                'identifier': parent_expasy_id,
            }
            rv[parent_expasy_id]['children'].append(rv[expasy_id]['concept'])

    return rv


def get_expasy_tree(path: Optional[str] = None, force_download: bool = False):
    """Populate the graph from a given specific file.

    :param path: The destination of the download
    :param force_download: True to force download
    """
    if path is None:
        path = download_expasy_tree(force_download=force_download)

    with open(path) as file:
        return lines_to_json(file)


if __name__ == '__main__':
    tree = get_expasy_tree()
    print(json.dumps(tree, indent=2))
