# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.constants import EXPASY, PROSITE, UNIPROT
from bio2bel_expasy.enrich import enrich_prosite_classes
from bio2bel_expasy.parser.tree import normalize_expasy_id
from pybel import BELGraph
from pybel.dsl import protein
from tests.constants import PopulatedDatabaseMixin

test_expasy_id = normalize_expasy_id('1.1.1.2')
test_subsubclass_id = normalize_expasy_id('1.1.1.-')
test_subclass_id = normalize_expasy_id('1.1.-.-')
test_class_id = normalize_expasy_id('1.-.-.-')


def expasy(name=None, identifier=None):
    return protein(namespace=EXPASY, name=name, identifier=identifier)


def prosite(name=None, identifier=None):
    return protein(namespace=PROSITE, name=name, identifier=identifier)


def uniprot(name=None, identifier=None):
    return protein(namespace=UNIPROT, name=name, identifier=identifier)


test_enzyme = expasy(name=test_expasy_id)
test_subsubclass = expasy(name=test_subsubclass_id)
test_subclass = expasy(name=test_subclass_id)
test_class = expasy(name=test_class_id)

test_prosite = prosite(identifier='PDOC00061')

test_protein_a = uniprot(name='A1A1A_DANRE', identifier='Q6AZW2')
test_protein_b = uniprot(name='A1A1B_DANRE', identifier='Q568L5')


class TestEnrich(PopulatedDatabaseMixin):
    """Tests that the enrichment functions work properly"""

    def test_enrich_enzyme_with_proteins(self):
        """Test that the edges from the enzyme to its proteins are added."""
        graph = BELGraph()
        node = graph.add_node_from_data(test_enzyme)

        self.assertIn(test_enzyme, graph, msg='Did not add test enzyme')
        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        self.manager.enrich_enzyme_with_proteins(graph, node)

        self.assertIn(test_protein_a, graph, msg=f'Did not add {test_protein_a}')
        self.assertIn(test_protein_b, graph, msg=f'Did not add {test_protein_b}')

        self.assertIn(test_enzyme, graph, msg='Lost test enzyme')
        self.assertIn(test_enzyme, graph[test_protein_a], msg='Did not add test edge')
        self.assertIn(test_enzyme, graph[test_protein_b], msg='Did not add test edge')

    def test_enrich_enzyme_children(self):
        """Test that the edges from the enzyme to its proteins are added."""
        graph = BELGraph()
        node = graph.add_node_from_data(test_class)

        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        self.manager.enrich_enzyme_children(graph, node)

        self.assertEqual(20, graph.number_of_nodes())  # 19 from enzclass_test.txt ans 1 from enzyme_test.dat
        self.assertEqual(19, graph.number_of_edges())

        self.assertIn(test_subclass, graph)
        self.assertIn(test_subsubclass, graph)
        self.assertIn(test_enzyme, graph)

    def test_enrich_proteins(self):
        """Test that the edges from proteins to their enzymes are added."""
        graph = BELGraph()
        graph.add_node_from_data(test_protein_a)
        graph.add_node_from_data(test_protein_b)

        self.assertEqual(2, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        self.manager.enrich_proteins_with_enzyme_families(graph)

        self.assertEqual(2, graph.number_of_edges(), msg='IS_A edges to parent node were not added')
        self.assertEqual(3, graph.number_of_nodes(),
                         msg='parent node was not added during Manager.enrich_proteins')

        self.assertIn(test_enzyme, graph,
                      msg='incorrect node was added: {}:{}'.format(list(graph)[0], graph.nodes[list(graph)[0]]))

        self.assertIn(test_protein_a, graph[test_enzyme])
        self.assertIn(test_protein_b, graph[test_enzyme])

    def test_prosite_classes(self):
        """Tests that the ProSites for enzymes are added"""
        graph = BELGraph()
        graph.add_node_from_data(test_enzyme)

        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        enrich_prosite_classes(graph=graph, manager=self.manager)

        self.assertEqual(2, graph.number_of_nodes())
        self.assertEqual(1, graph.number_of_edges())

        self.assertIn(test_prosite, graph)


if __name__ == '__main__':
    unittest.main()
