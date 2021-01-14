#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2021.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
import sys
import logging
import requests


def get_logging_level(level: str = 'INFO') -> logging:
    if level == 'DEBUG':
        return logging.DEBUG
    elif level == 'INFO':
        return logging.INFO
    elif level == 'WARN':
        return logging.WARN
    elif level == 'ERROR':
        return logging.ERROR
    elif level == 'CRITICAL':
        return logging.CRITICAL
    else:
        return logging.INFO


def load_logging(log_level: str, log_output: str = None, disabled: bool = False) -> logging:
    logging.basicConfig(format='%(asctime)s - [%(levelname)s] %(message)s',
                        level=get_logging_level(log_level),
                        datefmt='%d/%m/%Y %H:%M:%S')
    if log_output:
        file_handler = logging.FileHandler(log_output)
        logging.getLogger().addHandler(file_handler)

    if disabled:
        logging.disable(100)
    logging.debug(f"Logging level set to {log_level}")
    return logging


def print_and_exit(message: str) -> None:
    print(message)
    sys.exit()


def validate_inputs_outputs(inputfile: str or None = None,
                            outputfile: str or None = None) -> None:
    """
    Checks if the passed input/output files are valid and exist.

    :param inputfile: input file paths
    :param outputfile: output file paths
    :return: (side-effects)
    """

    if inputfile:
        if not os.path.isfile(inputfile):
            print_and_exit(f"Input file '{inputfile}' does not exist or it is not readable!")

    if outputfile:
        try:
            open(outputfile, "a").close()
        except IOError:
            print_and_exit(f"Output file '{outputfile}' cannot be opened or created!")


def download_taxonomy_dump(outfile, extension="zip") -> None:
    """
    Download Taxonomy Dump file from NCBI Taxonomy FTP server.

    :param outfile: Path to output file
    :param extension: (str) "zip" or "tar.gz"
    :return: (side-effects) writes file
    """

    if extension == "zip":
        url = "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdmp.zip"
    else:
        url = "http://ftp.ebi.ac.uk/pub/databases/ncbi/taxonomy/taxdmp.zip"
    r = requests.get(url, allow_redirects=True)
    if r.ok:
        open(outfile, 'wb').write(r.content)
    else:
        print(f"Unable to Download Taxonomy Dump from {url}")


def split_line(line) -> list:
    """Split a line from a dmp file"""
    return [x.strip() for x in line.split("	|")]


def parse_tax_ids(inputfile: str, sep: str or None = " ", indx: int = 0) -> list:
    """
    Parses a list of TaxIDs from an input file.
    It skips lines started with '#'.

    :param inputfile: Path to inputfile, which is a list of
        Taxonomy Identifiers
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: list of TaxIDs
    """

    tax_ids = []
    with open(inputfile, "r") as infile:
        for line in infile:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            if line != "":
                if sep:
                    tax_id = line.split(sep)[indx]
                else:
                    tax_id = line.split()[indx]
                if tax_id != "":
                    tax_ids.append(tax_id)
    return tax_ids


def get_all_children(node: dict or list, flatten: list, taxid: str) -> list:
    """
    Finds all the TaxIDs from a top node in the Taxonomy Tree.

    :param node: dict object
    :param flatten: list of TaxIDs
    :return: updated list of TaxIDs
    """

    if isinstance(node, dict):
        if taxid != node["id"]:
            flatten.append(node["id"])
        if "children" in node.keys():
            get_all_children(node["children"], flatten, taxid)
    elif isinstance(node, list):
        for d in node:
            get_all_children(d, flatten, taxid)
    return flatten
