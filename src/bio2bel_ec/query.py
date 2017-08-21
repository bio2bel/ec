# -*- coding: utf-8 -*-

import os

import pyuniprot
from pybel.constants import IS_A
from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import get_latest_arty_namespace

from .constants import EC_DATA_DIR


def get_data(taxid=9606, force=False):
    """
    :param taxid int
    :param force bool

    :return: pyuniprot.query.entry
    """
    if force:
        pyuniprot.update(taxids=[9606, 10090, 10116])

    query = pyuniprot.query()
    entries = query.entry(taxid=taxid)

    return entries


def print_human(file):
    """
    :param file file

    :return:
    """
    entries = get_data(9606)

    for e in entries:
        if e.ec_numbers:
            for ec in e.ec_numbers:
                print('p(HGNC:{}) {} p(EC:{})'.format(ensure_quotes(str(e.gene_name)), IS_A, ensure_quotes(str(ec))),
                      file=file)


def print_musmusculus(file):
    """
    :param file file

    :return:
    """
    entries = get_data(10090)

    for e in entries:
        if e.ec_numbers:
            for ec in e.ec_numbers:
                print('p(MGI:{}) {} p(EC:{})'.format(ensure_quotes(str(e.gene_name)), IS_A, ensure_quotes(str(ec))),
                      file=file)


def print_rattusnorvegicus(file):
    """
    :param file file

    :return:
    """
    entries = get_data(10116)

    for e in entries:
        if e.ec_numbers:
            for ec in e.ec_numbers:
                print('p(RGD:{}) {} p(EC:{})'.format(ensure_quotes(str(e.gene_name)), IS_A, ensure_quotes(str(ec))),
                      file=file)


def write_gene_ec_mapping(file):
    """Writes the hgnc to ec mapping bel script

    :param file file: A writable file or file-like
    :param pandas.DataFrame df: A data frame containing the original data source
    """

    write_boilerplate(
        document_name='HGNC Gene Family Definitions',
        authors='Aram Grigoryan',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents the gene families curated by HGNC, describing various functional, structural, and logical classifications""",
        namespace_dict={
            'ec': get_latest_arty_namespace('enzyme-class'),
            'HGNC': get_latest_arty_namespace('hgnc-gene-families'),
        },
        namespace_patterns={},
        annotations_dict={},
        annotations_patterns={},
        file=file
    )

    print('SET Citation = {{"URL","{}"}}'.format('http://www.uniprot.org/downloads'), file=file)
    print('SET Evidence = "HGNC to EC mapping"', file=file)

    print_human(file=file)
    print_musmusculus(file=file)
    print_rattusnorvegicus(file=file)


if __name__ == '__main__':
    filename = os.path.join(EC_DATA_DIR, 'hgnc_to_ec.bel')
    with open(filename, 'w') as f:
        write_gene_ec_mapping(f)
