# -*- coding: utf-8 -*-

import os

from bio2bel.utils import get_connection, get_data_dir

MODULE_NAME = 'expasy'
DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

#: TODO add docstring
EXPASY_TREE_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzclass.txt'
#: TODO add docstring
EXPASY_TREE_FILE = os.path.join(DATA_DIR, 'enzclass.txt')

#: TODO add docstring
EXPASY_DATABASE_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzyme.dat'
#: TODO add docstring
EXPASY_DATABASE_FILE = os.path.join(DATA_DIR, 'enzyme.dat')

EC_DATA_FILE_REGEX = '(ID   )(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PATTERN_REGEX = '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PROSITE_REGEX = '(PDOC|PS)(\d+)'
EC_DELETED_REGEX = 'Deleted entry'
EC_TRANSFERRED_REGEX = 'Transferred entry'

EXPASY = 'expasy'
PROSITE = 'prosite'
UNIPROT = 'up'

ENTRY_NAME = 'entry_name'
