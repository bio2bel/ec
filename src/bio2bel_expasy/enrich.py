# -*- coding: utf-8 -*-

import logging

from .manager import Manager

log = logging.getLogger(__name__)

__all__ = [
    'enrich_proteins',
    'enrich_prosite_classes',
    'enrich_enzymes'
]


def enrich_proteins(graph, connection=None):
    """Enriches proteins in the BEL graph with :data:`pybel.constants.IS_A` relations to their enzyme classes.

    1. Gets a list of UniProt proteins
    2. Annotates :data:`pybel.constants.IS_A` relations for all enzyme classes it finds

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_expasy.Manager
    """
    m = Manager.ensure(connection)
    return m.enrich_proteins_with_enzyme_families(graph)


def enrich_prosite_classes(graph, connection=None):
    """Enriches Enzyme classes for ProSite nodes in the graph.

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_expasy.Manager
    """
    m = Manager.ensure(connection=connection)
    return m.enrich_enzymes_with_prosites(graph)


def enrich_enzymes(graph, connection=None):
    """Add all children of entries (enzyme codes with 4 numbers in them that can be directly annotated to proteins)

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_expasy.Manager
    """
    m = Manager.ensure(connection=connection)
    return m.enrich_enzymes(graph)
