# -*- coding: utf-8 -*-

"""This library helps to download and parses the enzyme classes from the ExPASy ENZYME database.

Installation
------------
Easiest
~~~~~~~
Download the latest stable code from `PyPI <https://pypi.org/bio2bel_expasy>`_ with:

.. code-block:: sh

   $ python3 -m pip install bio2bel_expasy

Get the Latest
~~~~~~~~~~~~~~~
Download the most recent code from `GitHub <https://github.com/bio2bel/expasy>`_ with:

.. code-block:: sh

   $ python3 -m pip install git+https://github.com/bio2bel/expasy.git

For Developers
~~~~~~~~~~~~~~
Clone the repository from `GitHub <https://github.com/bio2bel/expasy>`_ and install in editable mode with:

.. code-block:: sh

   $ git clone https://github.com/bio2bel/expasy.git
   $ cd expasy
   $ python3 -m pip install -e .


Testing
-------
Bio2BEL ExPASy is tested with Python3 on Linux using `Travis CI <https://travis-ci.org/bio2bel/expasy>`_.
"""

from . import cli
from .manager import Manager

__version__ = '0.2.0'

__title__ = 'bio2bel_expasy'
__description__ = "A package for parsing and storing the ExPASy Enzyme Database"
__url__ = 'https://github.com/bio2bel/expasy'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2017-2018 Charles Tapley Hoyt'
