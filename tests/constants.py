# -*- coding: utf-8 -*-

import logging
import os
import tempfile
import unittest

from bio2bel_expasy import Manager

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

TREE_TEST_FILE = os.path.join(dir_path, 'enzclass_test.txt')
DATABASE_TEST_FILE = os.path.join(dir_path, 'enzyme_test.dat')


class TemporaryCacheClsMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fd, cls.path = tempfile.mkstemp()
        cls.connection = 'sqlite:///' + cls.path
        log.info('test database at %s', cls.connection)
        cls.manager = Manager(connection=cls.connection)
        cls.manager.create_all()

    @classmethod
    def tearDownClass(cls):
        cls.manager.session.close()
        os.close(cls.fd)
        os.remove(cls.path)


class PopulatedDatabaseMixin(TemporaryCacheClsMixin):
    @classmethod
    def setUpClass(cls):
        super(PopulatedDatabaseMixin, cls).setUpClass()
        cls.manager.populate(tree_path=TREE_TEST_FILE, database_path=DATABASE_TEST_FILE)
