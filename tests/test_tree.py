# -*- coding: utf-8 -*-

import unittest

from networkx import DiGraph

from bio2bel_expasy.parser.tree import get_tree, normalize_expasy_id
from tests.constants import TREE_TEST_FILE, TemporaryCacheClsMixin

DESCRIPTION = 'description'


class TestParseTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = get_tree(path=TREE_TEST_FILE)

    def test_tree_exists(self):
        self.assertIsInstance(self.tree, DiGraph)

    def test_has_nodes(self):
        x = normalize_expasy_id('1. -. -.-')
        self.assertIn(x, self.tree)
        self.assertIn(DESCRIPTION, self.tree.nodes[x])
        self.assertEqual('Oxidoreductases', self.tree.nodes[x][DESCRIPTION])

        x = normalize_expasy_id('1. 1. -.-')
        self.assertIn(x, self.tree)
        self.assertIn(DESCRIPTION, self.tree.nodes[x])
        self.assertEqual('Acting on the CH-OH group of donors', self.tree.nodes[x][DESCRIPTION])

        self.assertIn(normalize_expasy_id('1. 1. 1.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1. 2.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1. 3.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1. 4.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1. 5.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1. 9.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1.98.-'), self.tree)
        self.assertIn(normalize_expasy_id('1. 1.99.-'), self.tree)

        x = normalize_expasy_id('2. -. -.-')
        self.assertIn(x, self.tree)
        self.assertIn(DESCRIPTION, self.tree.nodes[x])
        self.assertEqual('Transferases', self.tree.nodes[x][DESCRIPTION])

        self.assertIn(normalize_expasy_id('2. 4.  2.-'), self.tree)
        self.assertIn(normalize_expasy_id('2. 4. 99.-'), self.tree)

    def test_has_edges(self):
        self.assertIn(normalize_expasy_id('1. 1. -.-'), self.tree[normalize_expasy_id('1. -. -.-')])
        self.assertIn(normalize_expasy_id('1. 1. 1.-'), self.tree[normalize_expasy_id('1. 1. -.-')])
        self.assertIn(normalize_expasy_id('1. 1. 2.-'), self.tree[normalize_expasy_id('1. 1. -.-')])
        self.assertIn(normalize_expasy_id('1. 1.99.-'), self.tree[normalize_expasy_id('1. 1. -.-')])
        self.assertIn(normalize_expasy_id('1. 2. -.-'), self.tree[normalize_expasy_id('1. -. -.-')])
        self.assertIn(normalize_expasy_id('1. 2. 1.-'), self.tree[normalize_expasy_id('1. 2. -.-')])
        self.assertIn(normalize_expasy_id('1. 2. 2.-'), self.tree[normalize_expasy_id('1. 2. -.-')])
        self.assertIn(normalize_expasy_id('1. 2.99.-'), self.tree[normalize_expasy_id('1. 2. -.-')])
        self.assertIn(normalize_expasy_id('2. 1. -.-'), self.tree[normalize_expasy_id('2. -. -.-')])
        self.assertIn(normalize_expasy_id('2. 1. 1.-'), self.tree[normalize_expasy_id('2. 1. -.-')])
        self.assertIn(normalize_expasy_id('2. 1. 5.-'), self.tree[normalize_expasy_id('2. 1. -.-')])
        self.assertIn(normalize_expasy_id('2. 2. -.-'), self.tree[normalize_expasy_id('2. -. -.-')])
        self.assertIn(normalize_expasy_id('2. 2. 1.-'), self.tree[normalize_expasy_id('2. 2. -.-')])
        self.assertIn(normalize_expasy_id('2. 3. -.-'), self.tree[normalize_expasy_id('2. -. -.-')])


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
        enzyme = self.manager.get_parent_by_expasy_id(expasy_id)
        self.assertIsNotNone(enzyme)
        self.assertEqual('1.2.-.-', enzyme.expasy_id)
        self.assertEqual('Acting on the aldehyde or oxo group of donors', enzyme.description)
