# -*- coding: utf-8 -*-

"""Utilities for Bio2BEL ExPASy."""

import logging

log = logging.getLogger(__name__)


def normalize_expasy_id(expasy_id: str) -> str:
    """Return a standardized ExPASy identifier string.

    :param expasy_id: A possibly non-normalized ExPASy identifier
    """
    return expasy_id.replace(" ", "")
