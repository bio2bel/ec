Bio2BEL ExPASy |build| |coverage| |docs| |zenodo|
=================================================
This repository downloads and parses the enzyme classes from the ExPASy ENZYME database

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``bio2bel_expasy`` can be installed easily from `PyPI <https://pypi.python.org/pypi/bio2bel_expasy>`_ with the
following code in your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install bio2bel_expasy

or from the latest code on `GitHub <https://github.com/bio2bel/expasy>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/bio2bel/expasy.git@master

or check the `installation instructions <http://bio2bel.readthedocs.io/projects/expasy/en/latest/#installation>`_.

Setup
-----
ExPASy can be downloaded and populated from either the Python REPL or the automatically installed command line
utility.

Python REPL
~~~~~~~~~~~
.. code-block:: python

    >>> import bio2bel_expasy
    >>> expasy_manager = bio2bel_expasy.Manager()
    >>> expasy_manager.populate()

Command Line Utility
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    bio2bel_expasy populate

Programmatic Interface
----------------------
To enrich the proteins in a BEL Graph with their enzyme classes, use:

>>> from bio2bel_expasy import enrich_proteins
>>> graph = ... # get a BEL graph
>>> enrich_proteins(graph)

Citations
---------
Gasteiger, E., *et al.* (2003). `ExPASy: The proteomics server for in-depth protein knowledge and analysis
<http://www.ncbi.nlm.nih.gov/pubmed/12824418>`_. Nucleic Acids Research, 31(13), 3784–8.


.. |build| image:: https://travis-ci.org/bio2bel/expasy.svg?branch=master
    :target: https://travis-ci.org/bio2bel/expasy
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/expasy/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/expasy?branch=master
    :alt: Coverage Status

.. |docs| image:: http://readthedocs.org/projects/bio2bel-expasy/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/ExPASy/en/latest/?badge=latest
    :alt: Documentation Status

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/bio2bel_expasy.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/bio2bel_expasy.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/bio2bel_expasy.svg
    :alt: Apache 2.0 License

.. |zenodo| image:: https://zenodo.org/badge/100023822.svg
    :target: https://zenodo.org/badge/latestdoi/100023822
