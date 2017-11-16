# -*- coding: utf-8 -*-

import os
import unittest

from bio2bel_expasy import tree
from bio2bel_expasy.constants import ENZCLASS_FILE, ENZCLASS_URL

test_path = ENZCLASS_FILE


class TestTree(unittest.TestCase):
    def setUp(self):
        if not os.path.isfile(ENZCLASS_FILE):
            tree.urlretrieve(ENZCLASS_URL, ENZCLASS_FILE)
        with open(test_path) as f:
            self.graph = tree.populate_tree()

    def test_length(self):
        """Assert that the number of nodes present in the test file is what we expect"""
        self.assertEqual(7549, self.graph.number_of_nodes())

    def test_node_existence(self):
        """Assert that the given nodes and their parent relationships are present"""
        self.assertIn(tree.standard_ec_id('5. 4. 2.-'), self.graph.edge[tree.standard_ec_id('5. 4. -.-')])

        self.assertIn(tree.standard_ec_id('6. 6. 1.-'), self.graph.edge[tree.standard_ec_id('6. 6. -.-')])
        self.assertIn(tree.standard_ec_id('6. 6. -.-'), self.graph.edge[tree.standard_ec_id('6. -. -.-')])


if __name__ == '__main__':
    unittest.main()
