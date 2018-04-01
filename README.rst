Bio2BEL ExPASy |build| |coverage| |docs|
========================================
This repository downloads and parses the enzyme classes from the ExPASy ENZYME database

Citation
--------
Gasteiger, E., Gattiker, A., Hoogland, C., Ivanyi, I., Appel, R. D., & Bairoch, A. (2003). ExPASy: The proteomics
server for in-depth protein knowledge and analysis. Nucleic Acids Research, 31(13), 3784–8. Retrieved from
http://www.ncbi.nlm.nih.gov/pubmed/12824418

Abstract
--------
The ExPASy (the Expert Protein Analysis System) World Wide Web server (http://www.expasy.org), is provided as a
service to the life science community by a multidisciplinary team at the Swiss Institute of Bioinformatics (SIB).
It provides access to a variety of databases and analytical tools dedicated to proteins and proteomics. ExPASy
databases include SWISS-PROT and TrEMBL, SWISS-2DPAGE, PROSITE, ENZYME and the SWISS-MODEL repository. Analysis tools
are available for specific tasks relevant to proteomics, similarity searches, pattern and profile searches,
post-translational modification prediction, topology prediction, primary, secondary and tertiary structure analysis
and sequence alignment. These databases and tools are tightly interlinked: a special emphasis is placed on integration
of database entries with related resources developed at the SIB and elsewhere, and the proteomics tools have been
designed to read the annotations in SWISS-PROT in order to enhance their predictions. ExPASy started to operate in
1993, as the first WWW server in the field of life sciences. In addition to the main site in Switzerland, seven
mirror sites in different continents currently serve the user community.

Installation
------------
:code:`python3 -m pip install git+https://github.com/bio2bel/expasy.git`

Command Line Interface
----------------------
To output the hierarchy of enzyme classes, type the following in the command line:

:code:`bio2bel_expasy write -f ~/Desktop/ec.bel`

Programmatic Interface
----------------------
To enrich the proteins in a BEL Graph with their enzyme classes, use:

>>> from bio2bel_expasy import enrich_proteins
>>> graph = ... # get a BEL graph
>>> enrich_proteins(graph)


.. |build| image:: https://travis-ci.org/bio2bel/expasy.svg?branch=master
    :target: https://travis-ci.org/bio2bel/expasy
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/expasy/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/expasy?branch=master
    :alt: Coverage Status

.. |docs| image:: http://readthedocs.org/projects/bio2bel-expasy/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/ExPASy/en/latest/?badge=latest
    :alt: Documentation Status
