# -*- coding: utf-8 -*-

def standard_ec_id(ns_ec_id):
    """Returns a standardized expasy id string

    :param str ns_ec_id: str
    :rtype: str
    """
    return ns_ec_id.replace(" ", "")


def non_standard_ec_id(s_ec_id):
    """Returns non canonical way of given expasy_id found in hierarchy data file.

    :param str s_ec_id: A standardized enzyme class string
    :rtype: str
    """
    nums = s_ec_id.split('.')
    ns_ec_id = ''
    for obj in nums:
        if obj.isdigit():
            if int(obj) > 9:
                ns_ec_id += obj
                ns_ec_id += '.'
            else:
                ns_ec_id += ' '
                ns_ec_id += obj
                ns_ec_id += '.'
        else:
            ns_ec_id += ' '
            ns_ec_id += obj
            ns_ec_id += '.'

    k = ns_ec_id.rfind(' ')
    ns_ec_id = ns_ec_id[:k] + ns_ec_id[k + 1:]
    return ns_ec_id.strip().strip('.')
