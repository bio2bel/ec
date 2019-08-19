# -*- coding: utf-8 -*-

"""SQLAlchemy models for Bio2BEL ExPASy."""

from __future__ import annotations

import pybel.dsl
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import backref, relationship

from .constants import MODULE_NAME, PROSITE, UNIPROT

ENZYME_CATEGORY_TABLE_NAME = f'{MODULE_NAME}_enzymeCategory'
ENZYME_SUPERFAMILY_TABLE_NAME = f'{MODULE_NAME}_enzymeSuperFamily'
ENZYME_FAMILY_TABLE_NAME = f'{MODULE_NAME}_enzymeFamily'
ENZYME_TABLE_NAME = f'{MODULE_NAME}_enzyme'
PROTEIN_TABLE_NAME = f'{MODULE_NAME}_protein'
PROSITE_TABLE_NAME = f'{MODULE_NAME}_prosite'
ENZYME_PROSITE_TABLE_NAME = f'{MODULE_NAME}_enzyme_prosite'
ENZYME_PROTEIN_TABLE_NAME = f'{MODULE_NAME}_enzyme_protein'

Base: DeclarativeMeta = declarative_base()

enzyme_prosite = Table(
    ENZYME_PROSITE_TABLE_NAME,
    Base.metadata,
    Column('enzyme_id', Integer, ForeignKey(f'{ENZYME_TABLE_NAME}.id'), primary_key=True),
    Column('prosite_id', Integer, ForeignKey(f'{PROSITE_TABLE_NAME}.id'), primary_key=True),
)

enzyme_protein = Table(
    ENZYME_PROTEIN_TABLE_NAME,
    Base.metadata,
    Column('enzyme_id', Integer, ForeignKey(f'{ENZYME_TABLE_NAME}.id'), primary_key=True),
    Column('protein_id', Integer, ForeignKey(f'{PROTEIN_TABLE_NAME}.id'), primary_key=True),
)

class EnzymeCategory(Base):
    """First level entry."""

    __tablename__ = ENZYME_CATEGORY_TABLE_NAME
    id = Column(Integer, primary_key=True)

    expasy_id = Column(String(16), unique=True, index=True, nullable=False, doc='The ExPASy enzyme code.')


class EnzymeSuperFamily(Base):
    """Second level Entry."""

    __tablename__ = ENZYME_SUPERFAMILY_TABLE_NAME
    id = Column(Integer, primary_key=True)

    expasy_id = Column(String(16), unique=True, index=True, nullable=False, doc='The ExPASy enzyme code.')
    parent_id = Column(Integer, ForeignKey(f'{EnzymeCategory.__tablename__}.id'), nullable=True)


class EnzymeFamily(Base):
    """Third level entry"""

    __tablename__ = ENZYME_FAMILY_TABLE_NAME
    id = Column(Integer, primary_key=True)

    expasy_id = Column(String(16), unique=True, index=True, nullable=False, doc='The ExPASy enzyme code.')
    parent_id = Column(Integer, ForeignKey(f'{EnzymeSuperFamily.__tablename__}.id'), nullable=True)


class Enzyme(Base):
    """ExPASy's main entry."""

    __tablename__ = ENZYME_TABLE_NAME
    id = Column(Integer, primary_key=True)

    expasy_id = Column(String(16), unique=True, index=True, nullable=False, doc='The ExPASy enzyme code.')
    parent_id = Column(Integer, ForeignKey(f'{EnzymeFamily.__tablename__}.id'), nullable=True)

    description = Column(String(255), doc='The ExPASy enzyme description. May need context of parents.')

    children = relationship('Enzyme', backref=backref('parent', remote_side=[id]))

    bel_encoding = 'P'

    def as_bel(self) -> pybel.dsl.Protein:
        """Return a PyBEL node representing this enzyme."""
        return pybel.dsl.Protein(
            namespace=MODULE_NAME,
            name=self.description,
            identifier=self.expasy_id,
        )

    def __str__(self):
        return f'ec-code:{self.expasy_id} ! {self.description}'


class Prosite(Base):
    """Maps ec to prosite entries."""

    __tablename__ = PROSITE_TABLE_NAME
    id = Column(Integer, primary_key=True)

    prosite_id = Column(String(255), unique=True, index=True, nullable=False, doc='ProSite Identifier')

    enzymes = relationship('Enzyme', secondary=enzyme_prosite, backref=backref('prosites'))

    bel_encoding = 'GRP'

    def as_bel(self) -> pybel.dsl.Protein:
        """Return a PyBEL node data dictionary representing this ProSite entry."""
        return pybel.dsl.Protein(
            namespace=PROSITE,
            identifier=str(self.prosite_id)
        )

    def __str__(self):
        return f'prosite:{self.prosite_id}'


class Protein(Base):
    """Maps enzyme to SwissProt or UniProt."""

    __tablename__ = PROTEIN_TABLE_NAME
    id = Column(Integer, primary_key=True)

    uniprot_id = Column(String(255), doc='UniProt `entry name <http://www.uniprot.org/help/entry_name>`_.')
    uniprot_accession = Column(String(255),
                               doc='UniProt `accession number <http://www.uniprot.org/help/accession_numbers>`_')

    enzymes = relationship('Enzyme', secondary=enzyme_protein, backref=backref('proteins'))

    bel_encoding = 'GRP'

    def as_bel(self) -> pybel.dsl.Protein:
        """Return a PyBEL node data dictionary representing this UniProt entry."""
        return pybel.dsl.Protein(
            namespace=UNIPROT,
            name=self.uniprot_accession,
            identifier=self.uniprot_id,
        )

    def __str__(self):
        return f'uniprot:{self.uniprot_id}'
