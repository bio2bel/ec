# -*- coding: utf-8 -*-

"""ExPASy database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.dsl import protein
from .constants import EXPASY, PROSITE, UNIPROT

TABLE_PREFIX = 'expasy'
ENZYME_TABLE_NAME = '{}_enzyme'.format(TABLE_PREFIX)
PROTEIN_TABLE_NAME = '{}_protein'.format(TABLE_PREFIX)
PROSITE_TABLE_NAME = '{}_prosite'.format(TABLE_PREFIX)
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

    expasy_id = Column(String(16), unique=True, index=True, nullable=False, doc='The ExPASy enzyme code.')
    description = Column(String(255), doc='The ExPASy enzyme description. May need context of parents.')

    parent_id = Column(Integer, ForeignKey('{}.id'.format(ENZYME_TABLE_NAME)), nullable=True)
    children = relationship('Enzyme', backref=backref('parent', remote_side=[id]))

    def __str__(self):
        return self.expasy_id

    def __repr__(self):
        return self.expasy_id

    @property
    def level(self):
        """Says what level (1, 2, 3, or 4) this enzyme is based on the number of dashes in its id

        :rtype: int
        """
        return 4 - self.expasy_id.count('-')

    def to_json(self):
        """Returns the data from this model as a dictionary

        :rtype: dict
        """
        return dict(
            expasy_id=self.expasy_id,
            description=self.description
        )

    def serialize_to_bel(self):
        """Returns a PyBEL node data dictionary representing this enzyme

        :return: dict
        """
        return protein(
            namespace=EXPASY,
            name=str(self.expasy_id),
            identifier=str(self.expasy_id)
        )


class Prosite(Base):
    """Maps ec to prosite entries"""
    __tablename__ = PROSITE_TABLE_NAME

    id = Column(Integer, primary_key=True)

    prosite_id = Column(String(255), unique=True, index=True, nullable=False, doc='ProSite Identifier')

    enzymes = relationship('Enzyme', secondary=enzyme_prosite, backref=backref('prosites'))

    def __str__(self):
        return self.prosite_id

    def serialize_to_bel(self):
        """Returns a PyBEL node data dictionary representing this ProSite entry

        :return: dict
        """
        return protein(
            namespace=PROSITE,
            identifier=str(self.prosite_id)
        )


class Protein(Base):
    """Maps ec to swissprot or uniprot"""
    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    enzymes = relationship('Enzyme', secondary=enzyme_protein, backref=backref('proteins'))

    accession_number = Column(String(255),
                              doc='UniProt `accession number <http://www.uniprot.org/help/accession_numbers>`_')
    entry_name = Column(String(255), doc='UniProt `entry name <http://www.uniprot.org/help/entry_name>`_.')

    #  is_SwissProt = Column(Boolean) #True for SwissProt False for else (UniProt)

    def __str__(self):
        return self.accession_number

    def serialize_to_bel(self):
        """Returns a PyBEL node data dictionary representing this UniProt entry

        :return: dict
        """
        return protein(
            namespace=UNIPROT,
            name=str(self.entry_name),
            identifier=str(self.accession_number)
        )
