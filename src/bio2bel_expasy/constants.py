# -*- coding: utf-8 -*-

import os

from bio2bel import get_connection, get_data_dir

MODULE_NAME = 'expasy'
DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

#: The web location of the enzyme class tree document
EXPASY_TREE_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzclass.txt'
#: The local cache location where the enzyme class tree document is stored
EXPASY_TREE_DATA_PATH = os.path.join(DATA_DIR, 'enzclass.txt')

#: The web location of the ENZYME database document
EXPASY_DATABASE_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzyme.dat'
#: The local cache location where the ENZYME database document is stored
EXPASY_DATA_PATH = os.path.join(DATA_DIR, 'enzyme.dat')

EC_DATA_FILE_REGEX = '(ID   )(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PATTERN_REGEX = '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PROSITE_REGEX = '(PDOC|PS)(\d+)'
EC_DELETED_REGEX = 'Deleted entry'
EC_TRANSFERRED_REGEX = 'Transferred entry'

EXPASY = 'EC'
PROSITE = 'PROSITE'
UNIPROT = 'UP'

ENTRY_NAME = 'entry_name'
