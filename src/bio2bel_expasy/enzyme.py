# -*- coding: utf-8 -*-

import logging
import re

from .constants import EC_DELETED_REGEX, EC_PATTERN_REGEX, EC_PROSITE_REGEX, EC_TRANSFERRED_REGEX, ENZCLASS_DATA_FILE
from .tree import download_ec_data

__all__ = [
    'expasy_parser',
    'ID',
    'DE',
    'PR',
    'DR',
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

ec_pattern = re.compile(EC_PATTERN_REGEX)
deleted_pattern = re.compile(EC_DELETED_REGEX)
transferred_pattern = re.compile(EC_TRANSFERRED_REGEX)
prosite_pattern = re.compile(EC_PROSITE_REGEX)


def expasy_parser(path=None, force_download=False):
    download_ec_data(force_download)

    path = ENZCLASS_DATA_FILE if path is None else path

    with open(path, 'r') as enzclass_file:
        return expasy_parser_helper(enzclass_file)


def expasy_parser_helper(enzclass_file):
    """Parses the ExPASy database file. Returns a list of enzyme entry dictionaries

    :rtype: list[dict]
    """
    expasy_db = []
    ec_data_entry = {ID: ''}
    for line in enzclass_file:
        descriptor = line[:2]
        if descriptor == "//":
            if ec_data_entry[ID] != '':
                ec_data_entry[CC] = " ".join(ec_data_entry[CC].split())
                ec_data_entry[CA] = " ".join(ec_data_entry[CA].split())
                expasy_db.append(ec_data_entry)
                # log.info(" EC_ENTRY: {}".format(ec_data_entry))
            ec_data_entry = {
                ID: '',
                DE: '',
                AN: [],
                CA: '',
                CF: [],
                CC: '',
                PR: [],
                DR: [],
                'DELETED': False,
                'TRANSFERRED': []
            }
            continue
        if descriptor == CC and ec_data_entry[ID] == '':
            log.info(" SKIPPING: {}".format(line.strip()))
            continue

        # parsing
        if descriptor == ID:
            ec_data_entry[ID] = ec_pattern.search(line).group()
            continue
        elif descriptor == DE:
            ec_data_entry[DE] = line.split('   ')[1].strip()
            if deleted_pattern.search(line) is not None:
                ec_data_entry['DELETED'] = True
            if transferred_pattern.search(line) is not None:
                matches = ec_pattern.finditer(line)
                for ec_ in matches:
                    ec_data_entry['TRANSFERRED'].append(ec_.group())
        elif descriptor == AN:
            ec_data_entry[AN].append(line[5:-2])
        elif descriptor == CA:
            ec_data_entry[CA] += line[5:-1]
        elif descriptor == CF:
            for cf_ in line[5:-2].split("; "):
                ec_data_entry[CF].append(cf_)
        elif descriptor == CC:
            ec_data_entry[CC] += line[5:-1]
        elif descriptor == PR:
            ec_data_entry[PR].append(prosite_pattern.search(line).group())
        elif descriptor == DR:
            for dr_tuple in line[5:-2].split(';'):
                dr_tuple = dr_tuple.strip()
                ec_data_entry[DR].append({
                    'accession_number': dr_tuple.split(', ')[0],
                    'entry_name': dr_tuple.split(', ')[1]
                })
        else:
            log.warning(" Unknown Descriptor is found. Risk of missed data or corrupt/wrong file.")

    return expasy_db
