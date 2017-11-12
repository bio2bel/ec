# -*- coding: utf-8 -*-

"""This method has been eclipsed by direct database download"""

from __future__ import print_function

from pybel.resources.arty import get_latest_arty_namespace
from pybel.resources.document import make_knowledge_header


def write_gene_ec_mapping(file):
    """Writes the hgnc to ec mapping bel script

    :param file file: A writable file or file-like
    :param pandas.DataFrame df: A data frame containing the original data source
    """
    lines = make_knowledge_header(
        name='HGNC Gene Family Definitions',
        authors='Aram Grigoryan',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents the gene families curated by HGNC, describing various functional, structural, and logical classifications""",
        namespace_url={
            'ec': get_latest_arty_namespace('enzyme-class'),
            'HGNC': get_latest_arty_namespace('hgnc-gene-families'),
        },
        namespace_patterns={},
        annotation_url={},
        annotation_patterns={},
    )

    for line in lines:
        print(line, file=file)

    print('SET Citation = {{"URL","{}"}}'.format('http://www.uniprot.org/downloads'), file=file)
    print('SET Evidence = "HGNC to EC mapping"', file=file)

    raise NotImplementedError
