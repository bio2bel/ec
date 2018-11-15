# -*- coding: utf-8 -*-

"""SQLAlchemy models for Bio2BEL ExPASy."""

from typing import Mapping

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.dsl import protein
from .constants import EXPASY, PROSITE, UNIPROT, MODULE_NAME

ENZYME_TABLE_NAME = f'{MODULE_NAME}_enzyme'
PROTEIN_TABLE_NAME = f'{MODULE_NAME}_protein'
PROSITE_TABLE_NAME = f'{MODULE_NAME}_prosite'
ENZYME_PROSITE_TABLE_NAME = f'{MODULE_NAME}_enzyme_prosite'
ENZYME_PROTEIN_TABLE_NAME = f'{MODULE_NAME}_enzyme_protein'

Base: DeclarativeMeta = declarative_base()

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
    """ExPASy's main entry."""

    __tablename__ = ENZYME_TABLE_NAME

    id = Column(Integer, primary_key=True)

    expasy_id = Column(String(16), unique=True, index=True, nullable=False, doc='The ExPASy enzyme code.')
    description = Column(String(255), doc='The ExPASy enzyme description. May need context of parents.')

    parent_id = Column(Integer, ForeignKey('{}.id'.format(ENZYME_TABLE_NAME)), nullable=True)
    children = relationship('Enzyme', backref=backref('parent', remote_side=[id]))

    bel_encoding = 'GRP'

    @property
    def level(self) -> int:
        """Return what level (1, 2, 3, or 4) this enzyme is based on the number of dashes in its id."""
        return 4 - self.expasy_id.count('-')

    def to_json(self) -> Mapping:
        """Return the data from this model as a dictionary."""
        return dict(
            expasy_id=self.expasy_id,
            description=self.description
        )

    def as_bel(self) -> protein:
        """Return a PyBEL node representing this enzyme."""
        return protein(
            namespace=EXPASY,
            name=str(self.expasy_id),
            identifier=str(self.expasy_id)
        )

    def __str__(self):
        return self.expasy_id

    def __repr__(self):
        return self.expasy_id


class Prosite(Base):
    """Maps ec to prosite entries."""

    __tablename__ = PROSITE_TABLE_NAME

    id = Column(Integer, primary_key=True)

    prosite_id = Column(String(255), unique=True, index=True, nullable=False, doc='ProSite Identifier')

    enzymes = relationship('Enzyme', secondary=enzyme_prosite, backref=backref('prosites'))

    bel_encoding = 'GRP'

    def as_bel(self) -> protein:
        """Return a PyBEL node data dictionary representing this ProSite entry."""
        return protein(
            namespace=PROSITE,
            identifier=str(self.prosite_id)
        )

    def __str__(self):
        return self.prosite_id


class Protein(Base):
    """Maps enzyme to SwissProt or UniProt."""

    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    enzymes = relationship('Enzyme', secondary=enzyme_protein, backref=backref('proteins'))

    accession_number = Column(String(255),
                              doc='UniProt `accession number <http://www.uniprot.org/help/accession_numbers>`_')
    entry_name = Column(String(255), doc='UniProt `entry name <http://www.uniprot.org/help/entry_name>`_.')

    #  is_SwissProt = Column(Boolean) #True for SwissProt False for else (UniProt)

    bel_encoding = 'GRP'

    def as_bel(self) -> protein:
        """Return a PyBEL node data dictionary representing this UniProt entry."""
        return protein(
            namespace=UNIPROT,
            name=str(self.entry_name),
            identifier=str(self.accession_number)
        )

    def __str__(self):
        return self.accession_number
