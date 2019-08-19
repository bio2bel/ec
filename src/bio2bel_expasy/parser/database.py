# -*- coding: utf-8 -*-

import json
import logging
import os
from typing import Any, Iterable, Mapping, Optional

from bio2bel.downloading import make_downloader

from bio2bel_expasy.constants import EXPASY_DATABASE_URL, EXPASY_DATA_PATH, EXPASY_PARSED_PATH

__all__ = [
    'get_expasy_database',
]

log = logging.getLogger(__name__)

#: The identifier of the entry (One)
ID = 'ID'
#: Description (One)
DE = 'DE'
#: Additional names/synonyms (Many)
AN = 'AN'
#: Chemical Reaction String (One)
CA = 'CA'
#: Comments (One - consider as free text)
CC = 'CC'
#: List of cofactors? (Many)
CF = 'CF'
#: ProSite Identifier (optional) (Many)
PR = 'PR'
#: Reference to UniProt or SwissProt (Many)
DR = 'DR'

download_expasy_database = make_downloader(EXPASY_DATABASE_URL, EXPASY_DATA_PATH)


def get_expasy_database(path: Optional[str] = None, force_download: bool = False) -> Mapping[str, Any]:
    """Get the ExPASy database as a JSON object.

    :param path: path to the file
    :param force_download: True to force download resources
    :return: list of data containing dictionaries
    """
    if path is not None:
        with open(path) as file:
            return _get_expasy_database_helper(file)

    download_expasy_database(force_download=force_download)

    if os.path.exists(EXPASY_PARSED_PATH):
        with open(EXPASY_PARSED_PATH) as file:
            return json.load(file)

    with open(EXPASY_DATA_PATH) as file, open(EXPASY_PARSED_PATH, 'w') as parsed_file:
        rv = _get_expasy_database_helper(file)
        json.dump(rv, parsed_file, indent=2, sort_keys=True)

    return rv


def group_by_id(lines):
    groups = []

    for line in lines:  # TODO replace with itertools.groupby
        line = line.strip()

        if line.startswith('ID'):
            groups.append([])

        if not groups:
            continue

        descriptor = line[:2]
        value = line[5:]

        groups[-1].append((descriptor, value))

    return groups


def _get_expasy_database_helper(lines: Iterable[str]) -> Mapping:
    """Parse the ExPASy database file and returns a list of enzyme entry dictionaries

    :param lines: An iterator over the ExPASy database file or file-like
    """
    rv = {}

    for groups in group_by_id(lines):
        _, expasy_id = groups[0]

        rv[expasy_id] = ec_data_entry = {
            'concept': {
                'namespace': 'ec-code',
                'identifier': expasy_id,
            },
            'parent': {
                'namespace': 'ec-code',
                'identifier': expasy_id.rsplit('.', 1)[0] + '.-',
            },
            'synonyms': [],
            'cofactors': [],
            'domains': [],
            'proteins': [],
            'alt_ids': [],
        }

        for descriptor, value in groups[1:]:
            if descriptor == '//':
                continue
            elif descriptor == DE and value == 'Deleted entry.':
                continue
            elif descriptor == DE and value.startswith('Transferred entry: '):
                value = value[len('Transferred entry: '):].rstrip()
                ec_data_entry['transfer_id'] = value
            elif descriptor == DE:
                ec_data_entry['concept']['name'] = value.rstrip('.')
            elif descriptor == AN:
                ec_data_entry['synonyms'].append(value.rstrip('.'))
            elif descriptor == PR:
                value = value[len('PROSITE; '):-1]  # remove trailing comma
                ec_data_entry['domains'].append({
                    'namespace': 'prosite',
                    'identifier': value,
                })
            elif descriptor == DR:
                for uniprot_entry in value.replace(' ', '').split(';'):
                    if not uniprot_entry:
                        continue
                    uniprot_id, uniprot_accession = uniprot_entry.split(',')
                    ec_data_entry['proteins'].append(dict(
                        namespace='uniprot',
                        name=uniprot_accession,
                        identifier=uniprot_id,
                    ))

    for expasy_id, data in rv.items():
        transfer_id = data.pop('transfer_id', None)
        if transfer_id is not None:
            rv[expasy_id]['alt_ids'].append(transfer_id)

    return rv


if __name__ == '__main__':
    r = get_expasy_database()
