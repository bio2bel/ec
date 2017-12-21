# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.enrich import enrich_enzyme_classes, enrich_prosite_classes
from bio2bel_expasy.parser.tree import standard_ec_id
from pybel import BELGraph
from pybel.dsl import protein
from tests.constants import PopulatedDatabaseMixin

test_expasy_id = standard_ec_id('1.1.1.2')
test_subsubclass_id = standard_ec_id('1.1.1.-')
test_subclass_id = standard_ec_id('1.1.-.-')
test_class_id = standard_ec_id('1.-.-.-')

test_entry = protein(name=test_expasy_id, namespace='EXPASY')
test_subsubclass = protein(name=test_subsubclass_id, namespace='EXPASY')
test_subclass = protein(name=test_subclass_id, namespace='EXPASY')
test_class = protein(name=test_class_id, namespace='EXPASY')

test_prosite = protein(identifier='PDOC00061', namespace='PROSITE')


class TestEnrich(PopulatedDatabaseMixin):
    def test_enrich_class(self):
        """Tests that the connection from the subclass to the enzyme class is inferred"""
        graph = BELGraph()
        graph.add_node_from_data(test_entry)
        self.assertEqual(1, graph.number_of_nodes())
        graph = enrich_enzyme_classes(graph)
        self.assertTrue(graph.has_node_with_data(test_subclass))

    def test_prosite_classes(self):
        """Tests prosite enrichment

        :return:
        """
        graph = BELGraph()
        graph.add_node_from_data(test_entry)

        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        enrich_prosite_classes(graph=graph)

        self.assertEqual(2, graph.number_of_nodes())
        self.assertEqual(1, graph.number_of_edges())

        self.assertTrue(graph.has_node_with_data(test_prosite))
