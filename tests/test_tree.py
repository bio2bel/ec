import os
import unittest

from bio2bel_ec import tree
from bio2bel_ec.constants import ENZCLASS_FILE, ENZCLASS_URL

test_path = ENZCLASS_FILE


class TestTree(unittest.TestCase):
    def setUp(self):
        if not os.path.isfile(ENZCLASS_FILE):
            tree.urlretrieve(ENZCLASS_URL, ENZCLASS_FILE)
        with open(test_path) as f:
            self.graph = tree.populate_tree()

    def TestLenght(self):
        self.assertEqual(33, self.graph.number_of_nodes())

    def test_1(self):
            """checks some nodes"""
            self.assertIn('5. 4. 2.-', self.graph.edge['5. 4. -.-'])

            self.assertIn('6. 6. 1.-', self.graph.edge['6. 6. -.-'])
            self.assertIn('6. 6. -.-', self.graph.edge['6. -. -.-'])

if __name__ == '__main__':
    unittest.main()