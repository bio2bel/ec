import os
import unittest



from ..src import tree
test_path = tree.ENZCLASS_FILE

class TestTree(unittest.TestCase):
    def setUp(self):
        if not os.path.isfile(tree.ENZCLASS_FILE):
            tree.urlretrieve(tree.ENZCLASS_URL, tree.ENZCLASS_FILE)
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