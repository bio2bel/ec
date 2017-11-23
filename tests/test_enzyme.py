# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.enzyme import expasy_parser
from tests.constants import ENZCLASS_DATA_FILE


class TestEnzyme(unittest.TestCase):
    def test_all(self):
        """Tests everything for the ENZCLASS_DATA_TEST_FILE

        :return: None
        """
        db = expasy_parser(ENZCLASS_DATA_FILE)
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
        self.assertEqual('A1A1A_DANRE', db[0]['DR'][0]['Entry_name'])
        self.assertEqual('Q568L5', db[0]['DR'][1]['accession_number'])
        self.assertEqual('A1A1B_DANRE', db[0]['DR'][1]['Entry_name'])
        self.assertEqual('Q24857', db[0]['DR'][2]['accession_number'])
        self.assertEqual('ADH3_ENTHI', db[0]['DR'][2]['Entry_name'])
        self.assertEqual('Q04894', db[0]['DR'][3]['accession_number'])
        self.assertEqual('ADH6_YEAST', db[0]['DR'][3]['Entry_name'])
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


if __name__ == '__main__':
    unittest.main()
