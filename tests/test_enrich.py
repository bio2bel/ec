# -*- coding: utf-8 -*-

import os
import unittest

from pybel import BELGraph
from pybel.constants import PROTEIN

from bio2bel_ec.enrich import enrich_enzyme_classes, get_parent

#ec = '1.14.99.1'
ec_p = '1.14.99.-'
ec_pp = '1.14. -.-'
ec_ppp = '1. -. -.-'

cyclooxygenase = PROTEIN, 'HGNC', 'PTGS2'
#cyclooxygenase_ec = PROTEIN, 'EC', ec
cyclooxygenase_ec_p = PROTEIN, 'EC', ec_p
cyclooxygenase_ec_pp = PROTEIN, 'EC', ec_pp
cyclooxygenase_ec_ppp = PROTEIN, 'EC', ec_ppp


class TestParent(unittest.TestCase):
    """Tests that the function for getting the parent given an enzyme string works"""

    #def test_instance(self):
        #self.assertEqual(ec_p, get_parent(ec))

    def test_subclass(self):
        self.assertEqual(ec_pp, get_parent(ec_p))

    def test_class(self):
        self.assertEqual(ec_ppp, get_parent(ec_pp))


@unittest.skipIf('CI' in os.environ, "Don't have PyUniProt data on Travis")
class TestEnrich(unittest.TestCase):
    def test_enrich_class(self):
        """Tests that the connection from the subclass to the enzyme class is inferred"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase_ec_pp)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        self.assertIn(cyclooxygenase_ec_pp, graph)
        self.assertIn(cyclooxygenase_ec_ppp, graph)

        self.assertIn(cyclooxygenase_ec_ppp, graph.edge[cyclooxygenase_ec_pp])

    def test_enrich_subclass(self):
        """Tests that the connection from the enzyme subsubclass to subclass and class is made and also
        the entire class hierarchy is ensured"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase_ec_p)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        self.assertIn(cyclooxygenase_ec_p, graph)
        self.assertIn(cyclooxygenase_ec_pp, graph)
        self.assertIn(cyclooxygenase_ec_ppp, graph)

        self.assertIn(cyclooxygenase_ec_pp, graph.edge[cyclooxygenase_ec_p])
        self.assertIn(cyclooxygenase_ec_ppp, graph.edge[cyclooxygenase_ec_pp])

    def test_enrich_instance(self):
        """Tests that the connection from the protein to the actual enzyme class is made and also
        the entire class hierarchy is ensured"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        #self.assertIn(cyclooxygenase_ec, graph)
        self.assertIn(cyclooxygenase_ec_p, graph)
        self.assertIn(cyclooxygenase_ec_pp, graph)
        self.assertIn(cyclooxygenase_ec_ppp, graph)

        #self.assertIn(cyclooxygenase_ec, graph.edge[cyclooxygenase])
        self.assertIn(cyclooxygenase_ec_p, graph.edge[cyclooxygenase_ec])
        self.assertIn(cyclooxygenase_ec_pp, graph.edge[cyclooxygenase_ec_p])
        self.assertIn(cyclooxygenase_ec_ppp, graph.edge[cyclooxygenase_ec_pp])


if __name__ == '__main__':
    unittest.main()
