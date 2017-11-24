# -*- coding: utf-8 -*-

import os

MODULE_NAME = 'expasy'
BIO2BEL_DIR = os.environ.get('BIO2BEL_DIRECTORY', os.path.join(os.path.expanduser('~'), '.pybel', 'bio2bel'))
DATA_DIR = os.path.join(BIO2BEL_DIR, MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CACHE_NAME = '{}.db'.format(MODULE_NAME)
DEFAULT_CACHE_PATH = os.path.join(DATA_DIR, DEFAULT_CACHE_NAME)
DEFAULT_CACHE_CONNECTION = os.environ.get('BIO2BEL_CONNECTION', 'sqlite:///' + DEFAULT_CACHE_PATH)

CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')

#: TODO add docstring
ENZCLASS_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzclass.txt'
#: TODO add docstring
ENZCLASS_FILE = os.path.join(DATA_DIR, 'enzclass.txt')

#: TODO add docstring
ENZCLASS_DATA_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzyme.dat'
#: TODO add docstring
ENZCLASS_DATA_FILE = os.path.join(DATA_DIR, 'enzyme.dat')

EC_DATA_FILE_REGEX = '(ID   )(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PATTERN_REGEX = '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PROSITE_REGEX = '(PDOC|PS)(\d+)'
EC_DELETED_REGEX = 'Deleted entry'
EC_TRANSFERRED_REGEX = 'Transferred entry'

EXPASY = 'expasy'
PROSITE = 'prosite'
UNIPROT = 'up'
