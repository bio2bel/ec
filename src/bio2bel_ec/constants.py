# -*- coding: utf-8 -*-

import os

from pybel.constants import PYBEL_DATA_DIR

ENZCLASS_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzclass.txt'
ENZCLASS_DATA_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzyme.dat'

ENZCLASS_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'expasy')

if not os.path.exists(ENZCLASS_DATA_DIR):
    os.makedirs(ENZCLASS_DATA_DIR)

ENZCLASS_FILE = os.path.join(ENZCLASS_DATA_DIR, 'enzclass.txt')
ENZCLASS_DATA_FILE = os.path.join(ENZCLASS_DATA_DIR, 'enzyme.dat')

EC_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'ec')
if not os.path.exists(EC_DATA_DIR):
    os.makedirs(EC_DATA_DIR)

EC_DATA_FILE_REGEX = '(ID   )(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'