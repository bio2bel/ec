# -*- coding: utf-8 -*-
"""ExPASy database model"""

from sqlalchemy import Column, String, Integer, Boolean, Table, ForeignKey
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

enzyme_hierarchy = Table(
    EC_TREE_TABLE_NAME,
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('{}.id'.format(EC_ENTRY_TABLE_NAME)), primary_key=True),
    Column('child_id', Integer, ForeignKey('{}.id'.format(EC_ENTRY_TABLE_NAME)), primary_key=True),
)
#TODO add docstrings for all columns in classes
class Enzyme_Entry(Base):
    """ExPASy's main entry"""
    __tablename__ = EC_ENTRY_TABLE_NAME

    id = Column(Integer, primary_key=True)
    enzyme_id = Column(String(255), secondary_key=True)
    description = Column(String(255))

    children = relationship(
        'Enzyme_Entry',
        secondary=enzyme_hierarchy,
        primaryjoin=(id == enzyme_hierarchy.c.parent_id),
        secondaryjoin=(id == enzyme_hierarchy.c.child_id)
    )

class Prosite_Entry(Base):
    """Maps ec to prosite entries"""
    __tablename__ = PROSITE_ENTRY_TABLE_NAME

    id=Column(Integer, primary_key=True)
    prosite_id = Column(String(255), secondary_key=True)
    enzyme_id = Column(String(255),foreignkey=True)

    ec = relationship(
        Enzyme_Entry,
        backref=backref(PROSITE_ENTRY_TABLE_NAME, uselist=True)
    )

class Protein_Entry(Base):
    """Maps ec to swissprot or uniprot"""
    __tablename__ = DR_ENTRY_TABLE_NAME

    id = Column(Integer, primary_key=True)
    enzyme_id = Column(String(255), foreignkey=True)
    AC_Nb = Column(String(255))
    Entry_name = Column(String(255))
    #  is_SwissProt = Column(Boolean) #True for SwissProt False for else (UniProt)

    ec = relationship(
        Enzyme_Entry,
        backref=backref(DR_ENTRY_TABLE_NAME, uselist=True)
    )