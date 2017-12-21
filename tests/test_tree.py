# -*- coding: utf-8 -*-

import unittest

from networkx import DiGraph

from bio2bel_expasy.parser.tree import get_tree, standard_ec_id
from tests.constants import TREE_TEST_FILE, TemporaryCacheClsMixin


class TestParseTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = get_tree(path=TREE_TEST_FILE)

    def test_tree_exists(self):
        self.assertIsInstance(self.tree, DiGraph)

    def test_has_nodes(self):
        x = standard_ec_id('1. -. -.-')
        self.assertIn(x, self.tree)
        self.assertIn('name', self.tree.node[x])
        self.assertEqual('Oxidoreductases', self.tree.node[x]['name'])

        x = standard_ec_id('1. 1. -.-')
        self.assertIn(x, self.tree)
        self.assertIn('name', self.tree.node[x])
        self.assertEqual('Acting on the CH-OH group of donors', self.tree.node[x]['name'])

        self.assertIn(standard_ec_id('1. 1. 1.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1. 2.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1. 3.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1. 4.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1. 5.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1. 9.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1.98.-'), self.tree)
        self.assertIn(standard_ec_id('1. 1.99.-'), self.tree)

        x = standard_ec_id('2. -. -.-')
        self.assertIn(x, self.tree)
        self.assertIn('name', self.tree.node[x])
        self.assertEqual('Transferases', self.tree.node[x]['name'])

        self.assertIn(standard_ec_id('2. 4.  2.-'), self.tree)
        self.assertIn(standard_ec_id('2. 4. 99.-'), self.tree)

    def test_has_edges(self):
        self.assertIn(standard_ec_id('1. 1. -.-'), self.tree.edge[standard_ec_id('1. -. -.-')])
        self.assertIn(standard_ec_id('1. 1. 1.-'), self.tree.edge[standard_ec_id('1. 1. -.-')])
        self.assertIn(standard_ec_id('1. 1. 2.-'), self.tree.edge[standard_ec_id('1. 1. -.-')])
        self.assertIn(standard_ec_id('1. 1.99.-'), self.tree.edge[standard_ec_id('1. 1. -.-')])
        self.assertIn(standard_ec_id('1. 2. -.-'), self.tree.edge[standard_ec_id('1. -. -.-')])
        self.assertIn(standard_ec_id('1. 2. 1.-'), self.tree.edge[standard_ec_id('1. 2. -.-')])
        self.assertIn(standard_ec_id('1. 2. 2.-'), self.tree.edge[standard_ec_id('1. 2. -.-')])
        self.assertIn(standard_ec_id('1. 2.99.-'), self.tree.edge[standard_ec_id('1. 2. -.-')])
        self.assertIn(standard_ec_id('2. 1. -.-'), self.tree.edge[standard_ec_id('2. -. -.-')])
        self.assertIn(standard_ec_id('2. 1. 1.-'), self.tree.edge[standard_ec_id('2. 1. -.-')])
        self.assertIn(standard_ec_id('2. 1. 5.-'), self.tree.edge[standard_ec_id('2. 1. -.-')])
        self.assertIn(standard_ec_id('2. 2. -.-'), self.tree.edge[standard_ec_id('2. -. -.-')])
        self.assertIn(standard_ec_id('2. 2. 1.-'), self.tree.edge[standard_ec_id('2. 2. -.-')])
        self.assertIn(standard_ec_id('2. 3. -.-'), self.tree.edge[standard_ec_id('2. -. -.-')])


class TestPopulateTree(TemporaryCacheClsMixin):
    @classmethod
    def setUpClass(cls):
        super(TestPopulateTree, cls).setUpClass()
        cls.manager.populate_tree(path=TREE_TEST_FILE)

    def test_get_class(self):
        enzyme = self.manager.get_enzyme_by_id('1. -. -.-')
        self.assertIsNotNone(enzyme)
        self.assertEqual('1.-.-.-', enzyme.expasy_id)
        self.assertEqual('Oxidoreductases', enzyme.description)

    def test_get_subclass(self):
        enzyme = self.manager.get_enzyme_by_id('1. 2. -.-')
        self.assertIsNotNone(enzyme)
        self.assertEqual('1.2.-.-', enzyme.expasy_id)
        self.assertEqual('Acting on the aldehyde or oxo group of donors', enzyme.description)

    def test_get_subsubclass(self):
        enzyme = self.manager.get_enzyme_by_id('1. 2. 1.-')
        self.assertIsNotNone(enzyme)
        self.assertEqual('1.2.1.-', enzyme.expasy_id)
        self.assertEqual('With NAD(+) or NADP(+) as acceptor', enzyme.description)

    def test_get_parent_of_subsubclass(self):
        expasy_id = '1. 2. 1.-'
        enzyme = self.manager.get_parent(expasy_id)
        self.assertIsNotNone(enzyme)
        self.assertEqual('1.2.-.-', enzyme.expasy_id)
        self.assertEqual('Acting on the aldehyde or oxo group of donors', enzyme.description)
