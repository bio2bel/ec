# -*- coding: utf-8 -*-

"""This library helps to download and parses the enzyme classes from the ExPASy ENZYME database.
It allows access to all important entries in the database via various query functions.
In addition it gives necessary functionality to enrich pybel.BELGraph graphs with relevant information.


ExPASy PubMed Reference: `12824418 <https://www.ncbi.nlm.nih.gov/pubmed/12824418>`_

``bio2bel_expasy`` will soon be installable from `PyPI <https://pypi.python.org/pypi/bio2bel_expasy>`_. In the mean
time, the latest code can be installed from `GitHub <https://github.com/bio2bel/expasy>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/bio2bel/expasy.git@master
"""

from . import cli
from .manager import Manager

__version__ = '0.1.1'

__title__ = 'bio2bel_expasy'
__description__ = "A package for parsing and storing the ExPASy Enzyme Database"
__url__ = 'https://github.com/bio2bel/expasy'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2017-2018 Charles Tapley Hoyt'
