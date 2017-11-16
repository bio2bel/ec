# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.enzyme import expasy_parser
from bio2bel_expasy.constants import ENZCLASS_FILE


class TestEnzyme(unittest.TestCase):
    def test_all(self):
        """Tests everything for the ENZCLASS_DATA_TEST_FILE

        :return: None
        """
        db = expasy_parser()
        #
        self.assertEqual(7177, len(db))
        #
        self.assertEqual(False, db[0]['DELETED'])
        self.assertEqual(0, len(db[0]['TRANSFERRED']))
        self.assertEqual('1.1.1.1', db[0]['ID'])
        self.assertEqual('Alcohol dehydrogenase.', db[0]['DE'])
        self.assertIn('Aldehyde reductase', db[0]['AN'])
        self.assertEqual('(1) An alcohol + NAD(+) = an aldehyde or ketone + NADH.(2) A secondary alcohol + NAD(+) = a ketone + NADH.', db[0]['CA'])
        self.assertIn('Zn(2+) or Fe cation', db[0]['CF'])
        self.assertIn('PDOC00058', db[0]['PR'])
        self.assertEqual('P07327', db[0]['DR'][0]['AC_Nb'])
        self.assertEqual('ADH1A_HUMAN', db[0]['DR'][0]['Entry_name'])
        self.assertEqual('P28469', db[0]['DR'][1]['AC_Nb'])
        self.assertEqual('ADH1A_MACMU', db[0]['DR'][1]['Entry_name'])
        self.assertEqual('Q5RBP7', db[0]['DR'][2]['AC_Nb'])
        self.assertEqual('ADH1A_PONAB', db[0]['DR'][2]['Entry_name'])
        self.assertEqual('P25405', db[0]['DR'][3]['AC_Nb'])
        self.assertEqual('ADH1A_SAAHA', db[0]['DR'][3]['Entry_name'])
        self.assertEqual(
            '-!- Acts on primary or secondary alcohols or hemi-acetals with very broad specificity; however the enzyme oxidizes methanol much more poorly than ethanol.-!- The animal, but not the yeast, enzyme acts also on cyclic secondary alcohols.',
            db[0]['CC'])
        #
        self.assertEqual('1.1.1.5', db[4]['ID'])
        self.assertEqual(False, db[4]['DELETED'])
        self.assertEqual(2, len(db[4]['TRANSFERRED']))
        self.assertIn('1.1.1.303', db[4]['TRANSFERRED'])
        self.assertIn('1.1.1.304', db[4]['TRANSFERRED'])
        #
        self.assertEqual('1.1.1.74', db[73]['ID'])
        self.assertEqual(True, db[73]['DELETED'])


if __name__ == '__main__':
    unittest.main()
