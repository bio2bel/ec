# -*- coding: utf-8 -*-

import unittest

from pybel import BELGraph
from pybel.constants import PROTEIN

from bio2bel_ec.enrich import enrich_enzyme_classes

cyclooxygenase = PROTEIN, 'HGNC', 'PTGS2'
cyclooxygenase_ec = PROTEIN, 'EC', '1.14.99.1'
cyclooxygenase_ec_p = PROTEIN, 'EC', '1.14.99.-'
cyclooxygenase_ec_pp = PROTEIN, 'EC', '1.14.-.-'
cyclooxygenase_ec_ppp = PROTEIN, 'EC', '1.-.-.-'


class TestEnrich(unittest.TestCase):
    def test_enrich(self):
        """Tests that the connection from the protein to the actual enzyme class is made and also
        the entire class hierarchy is ensured"""
        graph = BELGraph()
        graph.add_simple_node(*cyclooxygenase)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        self.assertIn(cyclooxygenase_ec, graph)
        self.assertIn(cyclooxygenase_ec_p, graph)
        self.assertIn(cyclooxygenase_ec_pp, graph)
        self.assertIn(cyclooxygenase_ec_ppp, graph)

        self.assertIn(cyclooxygenase_ec, graph.edge[cyclooxygenase])
        self.assertIn(cyclooxygenase_ec_p, graph.edge[cyclooxygenase_ec])
        self.assertIn(cyclooxygenase_ec_pp, graph.edge[cyclooxygenase_ec_p])
        self.assertIn(cyclooxygenase_ec_ppp, graph.edge[cyclooxygenase_ec_pp])
