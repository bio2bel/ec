# -*- coding: utf-8 -*-

import unittest

from bio2bel_expasy.parser.tree import normalize_expasy_id


class TestCanonicalize(unittest.TestCase):
    def test_entry(self):
        self.assertEqual('1.14.99.1', normalize_expasy_id('1.14.99.1'))

    def test_subsubclass(self):
        self.assertEqual('1.14.99.-', normalize_expasy_id('1.14.99.-'))
        self.assertEqual('1.1.1.-', normalize_expasy_id('1. 1. 1.-'))

    def test_subclass(self):
        self.assertEqual('1.14.99.-', normalize_expasy_id('1.14.99.-'))
        self.assertEqual('1.1.99.-', normalize_expasy_id('1. 1.99.-'))
        self.assertEqual('1.1.-.-', normalize_expasy_id('1. 1. -.-'))

    def test_class(self):
        self.assertEqual('1.-.-.-', normalize_expasy_id('1. -. -.-'))
