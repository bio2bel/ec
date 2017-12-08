# -*- coding: utf-8 -*-

import os
import logging
import unittest

from pybel import BELGraph
from pybel.constants import PROTEIN
from bio2bel.constants import DEFAULT_CACHE_PATH

from bio2bel_expasy.enrich import enrich_enzyme_classes, enrich_prosite_classes
from bio2bel_expasy.tree import standard_ec_id
from bio2bel_expasy.constants import EXPASY
from bio2bel_expasy.manager import Manager

test_expasy_id = standard_ec_id('1.1.1.1')
ec = standard_ec_id('1.14.99.1')
ec_p = standard_ec_id('1.14.99.-')
ec_pp = standard_ec_id('1.14. -.-')
ec_ppp = standard_ec_id('1. -. -.-')

dehydrogenase_test_expasy_id = PROTEIN, EXPASY, test_expasy_id
cyclooxygenase_ec = PROTEIN, EXPASY, ec
cyclooxygenase_ec_p = PROTEIN, EXPASY, ec_p
cyclooxygenase_ec_pp = PROTEIN, EXPASY, ec_pp
cyclooxygenase_ec_ppp = PROTEIN, EXPASY, ec_ppp


class TestCreation(unittest.TestCase):
    """tests connection and database creation"""

    def setUp(self):
        print(DEFAULT_CACHE_PATH)
        if not os.path.exists(DEFAULT_CACHE_PATH):
            self.m = Manager()
            print(DEFAULT_CACHE_PATH)
            self.m.populate()

    def test_creation(self):
        """if database created"""
        self.assertTrue(os.path.exists(DEFAULT_CACHE_PATH))


class TestTree(unittest.TestCase):
    """Tests that the function for getting the parent given an enzyme string works"""

    def setUp(self):
        self.m = Manager()

    def test_instance(self):
        self.assertEqual(ec_p, str(self.m.get_parent(ec)))

    def test_subclass(self):
        self.assertEqual(ec_pp, str(self.m.get_parent(ec_p)))

    def test_class(self):
        self.assertEqual(ec_ppp, str(self.m.get_parent(ec_pp)))


class TestEnrich(unittest.TestCase):
    def setUp(self):
        self.m = Manager()

    def test_enrich_class(self):
        """Tests that the connection from the subclass to the enzyme class is inferred"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase_ec_pp)

        self.assertEqual(1, graph.number_of_nodes())

        graph = enrich_enzyme_classes(graph)

        self.assertIn(cyclooxygenase_ec_pp, graph)
        # self.assertIn(cyclooxygenase_ec_ppp, graph)

        # self.assertIn(cyclooxygenase_ec_ppp, graph.edge[cyclooxygenase_ec_pp])

    def test_enrich_subclass(self):
        """Tests that the connection from the enzyme subsubclass to subclass and class is made and also
        the entire class hierarchy is ensured"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase_ec)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        self.assertIn(cyclooxygenase_ec_p, graph)
        self.assertIn(cyclooxygenase_ec_pp, graph)
        self.assertIn(cyclooxygenase_ec_ppp, graph)

    def test_enrich_instance(self):
        """Tests that the connection from the protein to the actual enzyme class is made and also
        the entire class hierarchy is ensured"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase_ec)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        self.assertIn(cyclooxygenase_ec, graph)
        self.assertIn(cyclooxygenase_ec_p, graph)
        self.assertIn(cyclooxygenase_ec_pp, graph)
        self.assertIn(cyclooxygenase_ec_ppp, graph)

        # self.assertIn(cyclooxygenase_ec_p, graph.edge[cyclooxygenase_ec])
        # self.assertIn(cyclooxygenase_ec_pp, graph.edge[cyclooxygenase_ec_p])
        # self.assertIn(cyclooxygenase_ec_ppp, graph.edge[cyclooxygenase_ec_pp])

    def test_prosite_classes(self):
        """Tests prosite enrichment

        :return:
        """
        graph = BELGraph()
        graph.add_simple_node(*dehydrogenase_test_expasy_id)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_prosite_classes(graph=graph)

        self.assertIn((PROTEIN, 'prosite', 'PDOC00058'), graph)


if __name__ == '__main__':
    logging.basicConfig(level=10)
    unittest.main()
