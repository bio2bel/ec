# -*- coding: utf-8 -*-

import os
import unittest

from bio2bel_expasy import tree
from tests.constants import ENZCLASS_FILE, ENZCLASS_DATA_FILE

#test_path = ENZCLASS_FILE


class TestTree(unittest.TestCase):
    def setUp(self):
        self.graph = tree.populate_tree(path_enzclass=ENZCLASS_FILE, path_enzclass_data=ENZCLASS_DATA_FILE, force_download=False)

    def test_length(self):
        """Assert that the number of nodes present in the test file is what we expect"""
        self.assertEqual(13, self.graph.number_of_nodes()) #  10 + 3

    def test_node_existence(self):
        """Assert that the given nodes and their parent relationships are present"""
        self.assertIn(tree.standard_ec_id('1. 1. -.-'), self.graph.edge[tree.standard_ec_id('1. -. -.-')])

        self.assertIn(tree.standard_ec_id('1. 1. 1.-'), self.graph.edge[tree.standard_ec_id('1. 1. -.-')])
        self.assertIn(tree.standard_ec_id('1. 1.99.-'), self.graph.edge[tree.standard_ec_id('1. 1. -.-')])


if __name__ == '__main__':
    unittest.main()
