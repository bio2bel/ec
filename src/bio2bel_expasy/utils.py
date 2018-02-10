# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


def normalize_expasy_id(expasy_id):
    """Returns a standardized ExPASy identifier string

    :param str expasy_id: A possibly non-normalized ExPASy identifier
    :rtype: str
    """
    return expasy_id.replace(" ", "")
