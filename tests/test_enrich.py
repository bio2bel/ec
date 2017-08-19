# -*- coding: utf-8 -*-

import os
import unittest

from pybel import BELGraph
from pybel.constants import PROTEIN

from bio2bel_ec.enrich import enrich_enzyme_classes


@unittest.skipIf('CI' in os.environ, "Don't have PyUniProt data on Travis")
class TestEnrich(unittest.TestCase):
    def setUp(self):
        self.cyclooxygenase = PROTEIN, 'HGNC', 'PTGS2'
        self.cyclooxygenase_ec = PROTEIN, 'EC', '1.14.99.1'
        self.cyclooxygenase_ec_p = PROTEIN, 'EC', '1.14.99.-'
        self.cyclooxygenase_ec_pp = PROTEIN, 'EC', '1.14.-.-'
        self.cyclooxygenase_ec_ppp = PROTEIN, 'EC', '1.-.-.-'

    def test_enrich(self):
        """Tests that the connection from the protein to the actual enzyme class is made and also
        the entire class hierarchy is ensured"""
        graph = BELGraph()
        graph.add_simple_node(*self.cyclooxygenase)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_enzyme_classes(graph)

        self.assertIn(self.cyclooxygenase_ec, graph)
        self.assertIn(self.cyclooxygenase_ec_p, graph)
        self.assertIn(self.cyclooxygenase_ec_pp, graph)
        self.assertIn(self.cyclooxygenase_ec_ppp, graph)

        self.assertIn(self.cyclooxygenase_ec, graph.edge[self.cyclooxygenase])
        self.assertIn(self.cyclooxygenase_ec_p, graph.edge[self.cyclooxygenase_ec])
        self.assertIn(self.cyclooxygenase_ec_pp, graph.edge[self.cyclooxygenase_ec_p])
        self.assertIn(self.cyclooxygenase_ec_ppp, graph.edge[self.cyclooxygenase_ec_pp])


if __name__ == '__main__':
    unittest.main()
