# -*- coding: utf-8 -*-
"""ExPASy database model"""

from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

TABLE_PREFIX = 'expasy'
ENTRY_TABLE_NAME = '{}_entry'.format(TABLE_PREFIX)
TREE_TABLE_NAME = '{}_tree'.format(TABLE_PREFIX)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

ec_hierarchy = Table(
    TREE_TABLE_NAME,
    Base.metadata,
    Column('ec_id', String, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=True),
    Column('description', String, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=False),
    Column('prosite_table_id', String, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=False, ForeignKey=True),
    Column('prot_table_id', String, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=False, ForeignKey=True),
)
