# -*- coding: utf-8 -*-

import re
import logging

log = logging.getLogger(__name__)
log.setLevel(20)
logging.basicConfig(level=20)

from bio2bel_ec.constants import ENZCLASS_DATA_FILE, EC_PATTERN_REGEX, EC_DELETED_REGEX, EC_TRANSFERRED_REGEX, EC_PROSITE_REGEX
from bio2bel_ec.tree import download_ec_data

__all__ = [
    'expasy_parser',
]

def expasy_parser():
    """
    Parses the ExPASy database file. Returns a list of enzyme entry dictionaries
    :return: list
    """

    download_ec_data()

    expasy_db = []

    with open(ENZCLASS_DATA_FILE, 'r') as enzclass_file:
        ec_data_entry = {'ID': ''}
        for line in enzclass_file:
            descriptor = line[:2]
            if descriptor == "//":
                if ec_data_entry['ID'] != '':
                    expasy_db.append(ec_data_entry)
                    #log.info(" EC_ENTRY: {}".format(ec_data_entry))
                ec_data_entry = {
                    'ID': '',
                    'DE': '',
                    'AN': [],
                    'CA': '',
                    'CF': [],
                    'CC': '',
                    'PR': [],
                    'DR': [],
                    'DELETED': False,
                    'TRANSFERRED': []
                }
                continue
            if descriptor == 'CC' and ec_data_entry['ID'] == '':
                log.info(" SKIPPING: {}".format(line.strip()))
                continue

            #parsing
            if descriptor == 'ID':
                ec_data_entry['ID'] = re.search(EC_PATTERN_REGEX, line).group()
                continue
            elif descriptor == 'DE':
                ec_data_entry['DE'] = line.split()[1].strip()
                if re.search(EC_DELETED_REGEX, line) is not None:
                    ec_data_entry['DELETED'] = True
                if re.search(EC_TRANSFERRED_REGEX, line.split()[1].strip()) is not None:
                    ec_data_entry['TRANSFERRED'] = re.search(EC_TRANSFERRED_REGEX, line.split()[1].strip()).group()
            elif descriptor == 'AN':
                ec_data_entry['AN'].append(line[5:-2])
            elif descriptor == 'CA':
                ec_data_entry['CA'] += line[5:-1]
            elif descriptor == 'CF':
                for cf_ in line[5:-2].split("; "):
                    ec_data_entry['CF'].append(cf_)
            elif descriptor == 'CC':
                ec_data_entry['CC'] += line[5:-1]
            elif descriptor == 'PR':
                ec_data_entry['PR'].append(re.search(EC_PROSITE_REGEX, line).group())
            elif descriptor == 'DR':
                for dr_tuple in line[5:-2].split(' ;  '):
                    ec_data_entry['DR'].append({'AC_Nb': dr_tuple.split(', ')[0], 'Entry_name': dr_tuple.split(', ')[1]})
            else:
                log.warning(" Unknown Descriptor is found. Risk of missed data or corrupt/wrong file.")

    return expasy_db



