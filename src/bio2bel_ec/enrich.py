# -*- coding: utf-8 -*-

from pybel_tools import pipeline

__all__ = [
    'enrich_enzyme_classes',
]


def get_parent(ec_str):
    """Get the parent enzyme string

    :param str ec_str: The child enzyme string
    :rtype: str
    """
    return NotImplementedError


@pipeline.mutator
def enrich_enzyme_classes(graph):
    """Enriches Enzyme Classes for proteins in the graph

    1. Gets a list of proteins
    2. looks up their entries with PyUniProt
    3. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds
    4. Ensures all parent enzyme classes for those enzyme classes

    :param pybel.BELGraph graph: A BEL graph
    """
    raise NotImplementedError
