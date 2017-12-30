# -*- coding: utf-8 -*-

from bio2bel_expasy.manager import Manager
from bio2bel_expasy.enrich import enrich_prosite_classes
from bio2bel_expasy.parser.tree import standard_ec_id
from pybel import BELGraph
from pybel.dsl import protein
from pybel.tokens import node_to_tuple
from tests.constants import PopulatedDatabaseMixin
from bio2bel_expasy.constants import EXPASY, PROSITE, UNIPROT

test_expasy_id = standard_ec_id('1.1.1.2')
test_subsubclass_id = standard_ec_id('1.1.1.-')
test_subclass_id = standard_ec_id('1.1.-.-')
test_class_id = standard_ec_id('1.-.-.-')

test_entry = protein(name=test_expasy_id, namespace=EXPASY)
test_tuple = node_to_tuple(test_entry)

test_subsubclass = protein(name=test_subsubclass_id, namespace=EXPASY)
test_subclass = protein(name=test_subclass_id, namespace=EXPASY)
test_class = protein(name=test_class_id, namespace=EXPASY)

test_prosite = protein(identifier='PDOC00061', namespace=PROSITE)

test_protein_a = protein(name='Q6AZW2', identifier='A1A1A_DANRE', namespace=UNIPROT)
test_protein_a_tuple = node_to_tuple(test_protein_a)
test_protein_b = protein(name='Q568L5', identifier='A1A1B_DANRE', namespace=UNIPROT)
test_protein_b_tuple = node_to_tuple(test_protein_b)


class TestEnrich(PopulatedDatabaseMixin):
    def setUp(self):
        self.manager = Manager()
        self.manager.ensure()
        #self.manager.populate()

    def test_enrich_class(self):
        """Tests that the edges from the enzyme to its proteins are added"""
        graph = BELGraph()
        graph.add_node_from_data(test_entry)

        self.assertEqual(1, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        self.manager.enrich_enzymes(graph)

        self.assertLess(1, graph.number_of_nodes())
        self.assertLess(0, graph.number_of_edges())

        self.assertTrue(graph.has_node_with_data(test_protein_a),
                        msg='missing protein that IS_A {}: {}'.format(test_entry, test_protein_a))
        self.assertTrue(graph.has_node_with_data(test_protein_b),
                        msg='missing protein that IS_A {}: {}'.format(test_entry, test_protein_b))

        self.assertIn(test_tuple, graph.edge[test_protein_a_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))
        self.assertIn(test_tuple, graph.edge[test_protein_a_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))

    def test_enrich_proteins(self):
        """Tests that the edges from proteins to their enzymes are added"""
        graph = BELGraph()
        graph.add_node_from_data(test_protein_a)
        graph.add_node_from_data(test_protein_b)

        self.assertEqual(2, graph.number_of_nodes())
        self.assertEqual(0, graph.number_of_edges())

        self.manager.enrich_proteins(graph)

        self.assertEqual(3, graph.number_of_nodes(), msg='parent node was not added during Manager.enrich_proteins')
        self.assertEqual(2, graph.number_of_edges(), msg='IS_A edges to parent node were not added')

        self.assertTrue(graph.has_node_with_data(test_entry),
                        msg='incorrect node was added: {}:{}'.format(list(graph)[0], graph.node[list(graph)[0]]))

        self.assertIn(test_tuple, graph.edge[test_protein_a_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))
        self.assertIn(test_tuple, graph.edge[test_protein_a_tuple],
                      msg='missing edge to {}'.format(test_protein_a_tuple))

    def test_prosite_classes(self):
        """Tests that the prosites for enzymes are added"""
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