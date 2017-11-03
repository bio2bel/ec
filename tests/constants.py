# -*- coding: utf-8 -*-

import os
from pybel.constants import PYBEL_DATA_DIR

dir_path = os.path.dirname(os.path.realpath(__file__))

ENZCLASS_DATA_TEST_FILE = os.path.join(dir_path, 'enzyme_test.dat')

ENZCLASS_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'expasy')
ENZCLASS_DATABASE_NAME = 'enzyme_dat_test.sqlite'
ENZCLASS_SQLITE_PATH = 'sqlite:///' + os.path.join(ENZCLASS_DATA_DIR, ENZCLASS_DATABASE_NAME)