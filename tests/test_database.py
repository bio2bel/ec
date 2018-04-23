# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.constants import ENTRY_NAME
from bio2bel_expasy.parser.database import get_expasy_database
from tests.constants import DATABASE_TEST_FILE, PopulatedDatabaseMixin


class TestParseEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = get_expasy_database(path=DATABASE_TEST_FILE)

    def test_all(self):
        """Tests everything for the ENZCLASS_DATA_TEST_FILE"""
        db = self.database
        #
        self.assertEqual(3, len(db))
        #
        self.assertEqual(False, db[0]['DELETED'])
        self.assertEqual(0, len(db[0]['TRANSFERRED']))
        self.assertEqual('1.1.1.2', db[0]['ID'])
        self.assertEqual('Alcohol dehydrogenase (NADP(+)).', db[0]['DE'])
        self.assertIn('Aldehyde reductase (NADPH)', db[0]['AN'])
        self.assertEqual('An alcohol + NADP(+) = an aldehyde + NADPH.', db[0]['CA'])
        self.assertIn('Zn(2+)', db[0]['CF'])
        self.assertIn('PDOC00061', db[0]['PR'])
        self.assertEqual('Q6AZW2', db[0]['DR'][0]['accession_number'])
        self.assertEqual('A1A1A_DANRE', db[0]['DR'][0][ENTRY_NAME])
        self.assertEqual('Q568L5', db[0]['DR'][1]['accession_number'])
        self.assertEqual('A1A1B_DANRE', db[0]['DR'][1][ENTRY_NAME])
        self.assertEqual('Q24857', db[0]['DR'][2]['accession_number'])
        self.assertEqual('ADH3_ENTHI', db[0]['DR'][2][ENTRY_NAME])
        self.assertEqual('Q04894', db[0]['DR'][3]['accession_number'])
        self.assertEqual('ADH6_YEAST', db[0]['DR'][3][ENTRY_NAME])
        self.assertEqual(
            '-!- Some members of this group oxidize only primary alcohols; others act also on secondary alcohols.-!- May be identical with EC 1.1.1.19, EC 1.1.1.33 and EC 1.1.1.55.-!- Re-specific with respect to NADPH.',
            db[0]['CC'])
        #
        self.assertEqual('1.1.1.5', db[1]['ID'])
        self.assertEqual(False, db[1]['DELETED'])
        self.assertEqual(2, len(db[1]['TRANSFERRED']))
        self.assertIn('1.1.1.303', db[1]['TRANSFERRED'])
        self.assertIn('1.1.1.304', db[1]['TRANSFERRED'])
        #
        self.assertEqual('1.1.1.74', db[2]['ID'])
        self.assertEqual(True, db[2]['DELETED'])


class TestPopulateDatabase(PopulatedDatabaseMixin):
    def test_has_parent(self):
        enzyme = self.manager.get_enzyme_by_id('1.1.1.2')
        self.assertIsNotNone(enzyme.parent)

    def test_has_children(self):
        enzyme = self.manager.get_enzyme_by_id('1.1.1.2')
        self.assertEqual(4, enzyme.level)
        self.assertEqual(0, len(enzyme.children), msg='level 4 should have no children')

    def test_get_protein(self):
        protein = self.manager.get_protein_by_uniprot_id('Q6AZW2')
        self.assertIsNotNone(protein)
        self.assertEqual('Q6AZW2', protein.accession_number)
        self.assertEqual('A1A1A_DANRE', protein.entry_name)

    def test_get_prosite(self):
        prosite = self.manager.get_prosite_by_id('PDOC00061')
        self.assertIsNotNone(prosite)
        self.assertEqual('PDOC00061', prosite.prosite_id)

    def test_get_entry(self):
        enzyme = self.manager.get_enzyme_by_id('1.1.1.2')
        self.assertIsNotNone(enzyme)
        self.assertEqual('1.1.1.2', enzyme.expasy_id)

        self.assertIsNotNone(enzyme.parent, msg="missing enzyme's parent")
        self.assertEqual('1.1.1.-', enzyme.parent.expasy_id)

        protein = self.manager.get_protein_by_uniprot_id('Q6AZW2')
        self.assertIn(protein, enzyme.proteins)

        prosite = self.manager.get_prosite_by_id('PDOC00061')
        self.assertIn(prosite, enzyme.prosites)
