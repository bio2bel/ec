# -*- coding: utf-8 -*-

import os

ENZCLASS_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzclass.txt'
ENZCLASS_DATA_URL = 'ftp://ftp.expasy.org/databases/enzyme/enzyme.dat'

BIO2BEL_DIR = os.environ.get('BIO2BEL_DIRECTORY', os.path.join(os.path.expanduser('~'), '.pybel', 'bio2bel'))
DATA_DIR = os.path.join(BIO2BEL_DIR, 'expasy')
os.makedirs(DATA_DIR, exist_ok=True)

ENZCLASS_FILE = os.path.join(DATA_DIR, 'enzclass.txt')
ENZCLASS_DATA_FILE = os.path.join(DATA_DIR, 'enzyme.dat')
ENZCLASS_DATA_TEST_FILE = os.path.join('../tests/', 'enzyme_test.dat')

ENZCLASS_CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')

DEFAULT_CACHE_NAME = 'enzyme_dat.sqlite'
DEFAULT_CACHE_PATH = os.path.join(DATA_DIR, DEFAULT_CACHE_NAME)
DEFAULT_CACHE_CONNECTION = os.environ.get('BIO2BEL_DB', 'sqlite:///' + DEFAULT_CACHE_PATH)

EC_DATA_FILE_REGEX = '(ID   )(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PATTERN_REGEX = '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PROSITE_REGEX = '(PDOC|PS)(\d+)'
EC_DELETED_REGEX = 'Deleted entry'
EC_TRANSFERRED_REGEX = 'Transferred entry'
SQL_DEFAULTS = "host='localhost', user='pyuniprot_user', passwd='pyuniprot_passwd', db='pyuniprot'"
SQLITE_DB_PATH = os.path.join('~/.pyuniprot/data/', 'pyuniprot.db')
