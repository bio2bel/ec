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
ENZCLASS_DATA_TEST_FILE = os.path.join('../tests/', 'enzyme_test.dat')

ENZCLASS_CONFIG_FILE_PATH = os.path.join(ENZCLASS_DATA_DIR, 'config.ini')

ENZCLASS_DATABASE_NAME = 'enzyme_dat.sqlite'
ENZCLASS_SQLITE_PATH = 'sqlite:///' + os.path.join(ENZCLASS_DATA_DIR, ENZCLASS_DATABASE_NAME)

EC_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'ec')
if not os.path.exists(EC_DATA_DIR):
    os.makedirs(EC_DATA_DIR)

EC_DATA_FILE_REGEX = '(ID   )(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PATTERN_REGEX = '(\d+|\-)\.( )*((\d+)|(\-))\.( )*(\d+|\-)(\.(n)?(\d+|\-))*'
EC_PROSITE_REGEX = '(PDOC|PS)(\d+)'
EC_DELETED_REGEX = 'Deleted entry'
EC_TRANSFERRED_REGEX = 'Transferred entry'
SQL_DEFAULTS = "host='localhost', user='pyuniprot_user', passwd='pyuniprot_passwd', db='pyuniprot'"
SQLITE_DB_PATH = os.path.join('~/.pyuniprot/data/', 'pyuniprot.db')