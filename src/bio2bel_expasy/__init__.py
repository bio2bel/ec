# -*- coding: utf-8 -*-
"""This library helps to download and pars the enzyme classes from the ExPASy ENZYME database.
It allows access to all important entries in the database via various query functions.
In addition it gives necessary functionality to enrich pybel.BELGraph graphs with relevant information.

"""

from . import cli
from .manager import Manager

__version__ = '0.1.1-dev'

__title__ = 'bio2bel_expasy'
__description__ = "A package for parsing the Expasy Enzyme Database"
__url__ = 'https://github.com/bio2bel/ec'

__author__ = 'Charles Tapley Hoyt and Aram Grigoryan'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2017 Charles Tapley Hoyt and Aram Grigoryan'
