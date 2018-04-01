# -*- coding: utf-8 -*-

import logging
import os

from bio2bel.testing import make_temporary_cache_class_mixin
from bio2bel_expasy import Manager

log = logging.getLogger(__name__)

HERE = os.path.dirname(os.path.realpath(__file__))

resources_directory_path = os.path.join(HERE, 'resources')

TREE_TEST_FILE = os.path.join(resources_directory_path, 'enzclass_test.txt')
DATABASE_TEST_FILE = os.path.join(resources_directory_path, 'enzyme_test.dat')

TemporaryCacheClsMixin = make_temporary_cache_class_mixin(Manager)


class PopulatedDatabaseMixin(TemporaryCacheClsMixin):
    @classmethod
    def setUpClass(cls):
        """Creates a persistent database and populates it with the test data included in the Bio2BEL ExPASy repository
        """
        super(PopulatedDatabaseMixin, cls).setUpClass()
        cls.manager.populate(tree_path=TREE_TEST_FILE, database_path=DATABASE_TEST_FILE)

    @classmethod
    def tearDownClass(cls):
        """Drops everything from the persistent database before tearing it down"""
        cls.manager.drop_all()
        super(PopulatedDatabaseMixin, cls).tearDownClass()
