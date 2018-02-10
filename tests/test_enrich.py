# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.constants import EXPASY, PROSITE, UNIPROT
from bio2bel_expasy.enrich import enrich_enzymes, enrich_prosite_classes, enrich_proteins
from bio2bel_expasy.parser.tree import normalize_expasy_id
from pybel import BELGraph
from pybel.dsl import protein
from pybel.tokens import node_to_tuple
from tests.constants import PopulatedDatabaseMixin

test_expasy_id = normalize_expasy_id('1.1.1.2')
test_subsubclass_id = normalize_expasy_id('1.1.1.-')
test_subclass_id = normalize_expasy_id('1.1.-.-')
test_class_id = normalize_expasy_id('1.-.-.-')


def expasy(name=None, identifier=None):
    return protein(namespace=EXPASY, name=name, identifier=identifier)


def prosite(name=None, identifier=None):
    return protein(namespace=PROSITE, name=name, identifier=identifier)


test_entry = expasy(name=test_expasy_id)
test_tuple = test_entry.as_tuple()

test_subsubclass = expasy(name=test_subsubclass_id)
test_subclass = expasy(name=test_subclass_id)
test_class = expasy(name=test_class_id)

test_prosite = prosite(identifier='PDOC00061')

test_protein_a = protein(name='A1A1A_DANRE', identifier='Q6AZW2', namespace=UNIPROT)
test_protein_a_tuple = test_protein_a.as_tuple()
test_protein_b = protein(name='A1A1B_DANRE', identifier='Q568L5', namespace=UNIPROT)
test_protein_b_tuple = test_protein_b.as_tuple()


class TestEnrich(PopulatedDatabaseMixin):
    """Tests that the enrichment functions work properly"""

    def test_get_entry(self):
        """Makes sure that this doesn't error out"""
        self.manager.get_enzyme_by_id('1.1.1.2')

    def test_enrich_class(self):
        """Tests that the edges from the enzyme to its proteins are added"""
        graph = BELGraph()
        graph.add_node_from_data(test_entry)

        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        enrich_enzymes(graph, connection=self.manager)

        self.assertLess(1, graph.number_of_nodes())
        self.assertLess(0, graph.number_of_edges())

        self.assertTrue(graph.has_node_with_data(test_protein_a),
                        msg='missing protein that IS_A {}: {}'.format(test_entry, test_protein_a))
        self.assertTrue(graph.has_node_with_data(test_protein_b),
                        msg='missing protein that IS_A {}: {}'.format(test_entry, test_protein_b))

        self.assertIn(test_protein_a_tuple, graph.edge[test_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))
        self.assertIn(test_protein_a_tuple, graph.edge[test_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))

    def test_enrich_proteins(self):
        """Tests that the edges from proteins to their enzymes are added"""
        graph = BELGraph()
        graph.add_node_from_data(test_protein_a)
        graph.add_node_from_data(test_protein_b)

        self.assertEqual(2, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        enrich_proteins(graph, connection=self.manager)

        self.assertEqual(3, graph.number_of_nodes(), msg='parent node was not added during Manager.enrich_proteins')
        self.assertEqual(2, graph.number_of_edges(), msg='IS_A edges to parent node were not added')

        self.assertTrue(graph.has_node_with_data(test_entry),
                        msg='incorrect node was added: {}:{}'.format(list(graph)[0], graph.node[list(graph)[0]]))

        self.assertIn(test_protein_a_tuple, graph.edge[test_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))
        self.assertIn(test_protein_b_tuple, graph.edge[test_tuple],
                      msg='missing edge to {}'.format(test_protein_b_tuple))

    def test_prosite_classes(self):
        """Tests that the ProSites for enzymes are added"""
        graph = BELGraph()
        graph.add_node_from_data(test_entry)

        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        enrich_prosite_classes(graph=graph)

        self.assertEqual(2, graph.number_of_nodes())
        self.assertEqual(1, graph.number_of_edges())

        self.assertTrue(graph.has_node_with_data(test_prosite))


if __name__ == '__main__':
    unittest.main()
