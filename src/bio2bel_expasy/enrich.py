# -*- coding: utf-8 -*-

"""Convenient wrapper functions for the manager."""

import logging
from typing import Optional

from pybel import BELGraph
from .manager import Manager

log = logging.getLogger(__name__)

__all__ = [
    'enrich_prosite_classes',
    'enrich_enzymes',
]


def enrich_prosite_classes(graph: BELGraph, manager: Optional[Manager] = None) -> None:
    """Enriches Enzyme classes for ProSite nodes in the graph."""
    if manager is None:
        manager = Manager()

    return manager.enrich_enzymes_with_prosites(graph)


def enrich_enzymes(graph: BELGraph, manager: Optional[Manager] = None) -> None:
    """Add all children of entries (enzyme codes with 4 numbers in them that can be directly annotated to proteins)."""
    if manager is None:
        manager = Manager()

    return manager.enrich_enzymes(graph)
