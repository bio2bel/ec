# -*- coding: utf-8 -*-

"""ExPASy database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

TABLE_PREFIX = 'expasy'
ENZYME_TABLE_NAME = '{}_enzyme'.format(TABLE_PREFIX)
PROTEIN_TABLE_NAME = '{}_protein'.format(TABLE_PREFIX)
PROSITE_TABLE_NAME = '{}_prosite'.format(TABLE_PREFIX)
TREE_TABLE_NAME = '{}_tree'.format(TABLE_PREFIX)
ENZYME_PROSITE_TABLE_NAME = '{}_enzyme_prosite'.format(TABLE_PREFIX)
ENZYME_PROTEIN_TABLE_NAME = '{}_enzyme_protein'.format(TABLE_PREFIX)

Base = declarative_base()

enzyme_prosite = Table(
    ENZYME_PROSITE_TABLE_NAME,
    Base.metadata,
    Column('enzyme_id', Integer, ForeignKey('{}.id'.format(ENZYME_TABLE_NAME)), primary_key=True),
    Column('prosite_id', Integer, ForeignKey('{}.id'.format(PROSITE_TABLE_NAME)), primary_key=True),
)

enzyme_protein = Table(
    ENZYME_PROTEIN_TABLE_NAME,
    Base.metadata,
    Column('enzyme_id', Integer, ForeignKey('{}.id'.format(ENZYME_TABLE_NAME)), primary_key=True),
    Column('protein_id', Integer, ForeignKey('{}.id'.format(PROTEIN_TABLE_NAME)), primary_key=True),
)


class Enzyme(Base):
    """ExPASy's main entry"""
    __tablename__ = ENZYME_TABLE_NAME

    id = Column(Integer, primary_key=True)

    expasy_id = Column(String(255), doc='The ExPAsY enzyme code')

    description = Column(String(255), doc='Description')

    parent_id = Column(Integer, ForeignKey('{}.id'.format(ENZYME_TABLE_NAME)), nullable=True)
    parent = relationship('Enzyme')

    #children = relationship(
    #    'Enzyme',
    #    secondary=enzyme_hierarchy,
    #    primaryjoin=(id == enzyme_hierarchy.c.parent_id),
    #    secondaryjoin=(id == enzyme_hierarchy.c.child_id)
    #)

    def __str__(self):
        return self.expasy_id


class Prosite(Base):
    """Maps ec to prosite entries"""
    __tablename__ = PROSITE_TABLE_NAME

    id = Column(Integer, primary_key=True)

    prosite_id = Column(String(255), doc='ProSite Identifier')

    enzymes = relationship('Enzyme', secondary=enzyme_prosite, backref=backref('prosites'))


class Protein(Base):
    """Maps ec to swissprot or uniprot"""
    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    enzymes = relationship('Enzyme', secondary=enzyme_protein, backref=backref('proteins'))

    accession_number = Column(String(255), doc='Swiss-Prot  primary accession  number of the entry to which reference is being made')
    Entry_name = Column(String(255), doc='Swiss-Prot entry name')
    #  is_SwissProt = Column(Boolean) #True for SwissProt False for else (UniProt)
