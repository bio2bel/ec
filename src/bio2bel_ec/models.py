# -*- coding: utf-8 -*-
"""ExPASy database model"""

from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

EC_TABLE_PREFIX = 'expasy'
EC_ENTRY_TABLE_NAME = '{}_entry'.format(EC_TABLE_PREFIX)
EC_TREE_TABLE_NAME = '{}_tree'.format(EC_TABLE_PREFIX)

PROSITE_TABLE_PREFIX = 'prosite'
PROSITE_ENTRY_TABLE_NAME = '{}_entry'.format(PROSITE_TABLE_PREFIX)
PROSITE_TREE_TABLE_NAME = '{}_tree'.format(PROSITE_TABLE_PREFIX)

DR_TABLE_PREFIX = 'uniprot-swissprot'
DR_ENTRY_TABLE_NAME = '{}_entry'.format(DR_TABLE_PREFIX)
DR_TREE_TABLE_NAME = '{}_tree'.format(DR_TABLE_PREFIX)


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

ec_hierarchy = Table(
    EC_TREE_TABLE_NAME,
    Base.metadata,
    Column('ec_id', String, ForeignKey('{}.id'.format(EC_ENTRY_TABLE_NAME)), primary_key=True),
    Column('de', String, ForeignKey('{}.id'.format(EC_ENTRY_TABLE_NAME)), primary_key=False),
)

pr_hierarchy = Table(
    PROSITE_TREE_TABLE_NAME,
    Base.metadata,
    Column('ec_id', String, '{}.id'.format(EC_ENTRY_TABLE_NAME), foreign_key=True),
    Column('pr_id', String, '{}.id'.format(PROSITE_ENTRY_TABLE_NAME), primary_key=True),
)

dr_hierarchy = Table(
    DR_TREE_TABLE_NAME,
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('ec_id', String, '{}.id'.format(EC_ENTRY_TABLE_NAME), foreign_key=True),
    Column('AC_Nb', String, '{}.id'.format(DR_ENTRY_TABLE_NAME)),
    Column('Entry_name', String, '{}.id'.format(DR_ENTRY_TABLE_NAME)),
    Column('comment', String)
)

class EC_Entry(Base):
    """ExPASy's main entry"""
    __tablename__ = EC_ENTRY_TABLE_NAME

    id = Column(String(255))

    de = Column(String(255))

    children = relationship(
        'EC_Entry',
        secondary=ec_hierarchy,
        primaryjoin=(id == ec_hierarchy.c.ec_id),
        secondaryjoin=(de == ec_hierarchy.c.de)
    )

class PR_Entry(Base):
    """Maps ec to prosite entries"""
    __tablename__ = PROSITE_ENTRY_TABLE_NAME

    id = Column(String(255))
    ec_id = Column(String(255),foreignkey=True)

    children = relationship(
        'PR_Entry',
        secondary=pr_hierarchy,
        primaryjoin=(id==pr_hierarchy.c.pr_id),
        secondaryjoin=(ec_id==pr_hierarchy.c.ec_id)
    )
    ec = relationship(
        EC_Entry,
        backref=backref(PROSITE_ENTRY_TABLE_NAME, uselist=True)
    )

class DR_Entry(Base):
    """Maps ec to swissprot or uniprot"""
    __tablename__ = DR_ENTRY_TABLE_NAME

    id = Column(Integer)
    ec_id = Column(String(255))
    AC_Nb = Column(String(255))
    Entry_name = Column(String(255))
    comment = Column(String(255)) #used to indicate UniProt or SWISSProt
    children = relationship(
        'DR_Entry',
        secondary=dr_hierarchy,
        primaryjoin=(id==dr_hierarchy.c.id),
        secondaryjoin=(ec_id==dr_hierarchy.c.ec_id)
    )
    ec = relationship(
        EC_Entry,
        backref=backref(DR_ENTRY_TABLE_NAME, uselist=True)
    )