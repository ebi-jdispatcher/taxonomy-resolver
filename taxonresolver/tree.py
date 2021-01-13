#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2021.
:license: Apache 2.0, see LICENSE for more details.
"""

import io
import pickle
import zipfile
import logging

from taxonresolver.utils import parse_tax_ids
from taxonresolver.utils import print_and_exit
from taxonresolver.utils import split_line
from taxonresolver.utils import download_taxonomy_dump
from taxonresolver.utils import get_all_children


def tree_reparenting(tree: dict) -> dict:
    """
    Loops over the Tree dictionary and re-parents every node to
    find all nodes children.

    :param tree: dict of node objects
    :return: dict object
    """

    # tree re-parenting
    for node in tree.values():
        if "children" not in tree[node["parent_id"]]:
            tree[node["parent_id"]]["children"] = []
        if node["id"] != node["parent_id"]:
            tree[node["parent_id"]]["children"].append(tree[node["id"]])
    return tree


def build_tree(inputfile: str) -> dict:
    """
    Given the path to NCBI Taxonomy 'taxdump.zip' file,
    builds a slim tree data structure.

    :param inputfile: Path to inputfile
    :return: dict object
    """

    tree = {}
    # read nodes
    if zipfile.is_zipfile(inputfile):
        with zipfile.ZipFile(inputfile) as taxdmp:
            dmp = taxdmp.open("nodes.dmp")
    else:
        dmp = open(inputfile, "rb")
    for line in io.TextIOWrapper(dmp):
        fields = split_line(line)
        tree[fields[0]] = {
            "id": fields[0],
            "parent_id": fields[1]
        }
    dmp.close()
    return tree_reparenting(tree)


def write_tree(tree: dict, outputfile: str) -> None:
    """
    Writes a Tree object to file.

    :param tree: dict object
    :param outputfile: Path to outputfile
    :return: (side-effects) writes to file
    """
    with open(outputfile, 'wb') as outfile:
        pickle.dump(tree, outfile)


def load_tree(inputfile: str) -> dict:
    """
    Loads a pre-existing Tree from file.

    :param inputfile: Path to outputfile
    :return: dict object
    """
    return pickle.load(open(inputfile, "rb"))


def search_taxids(tree: dict, searchids: list or str,
                  filterids: list or str or None = None,
                  sep: str = None, indx: int = 0) -> list:
    """
    Searches an existing Tree and produces a list of TaxIDs.
    Checks if TaxID is in the list, if so provides as is, else,
        searches all children in the list that compose that node,
        (i.e. finds it's leaves)

    :param tree: dict object
    :param searchids: list of TaxIDs or Path to file with TaxIDs to search with
    :param filterids: list of TaxIDs or None or Path to inputfile,
        which is a list of TaxIDs (optional)
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: list of TaxIDs
    """

    if type(searchids) is list:
        taxids_search = searchids
    elif type(searchids) is str:
        taxids_search = parse_tax_ids(searchids)
    taxids_found = taxids_search[:]
    for taxid in taxids_search:
        if taxid in tree:
            get_all_children(tree[taxid], taxids_found, taxid)

    taxids_filter = []
    if type(filterids) is list:
        taxids_filter = filterids
    elif type(filterids) is str:
        taxids_filter = parse_tax_ids(filterids, sep, indx)
    if taxids_filter:
        taxids_found = [tax_id for tax_id in taxids_found if tax_id in taxids_filter]
    return list(set(taxids_found))


def validate_taxids(tree: dict, validateids: list or str or None) -> bool:
    """
    Checks if TaxIDs are in the list and in the Tree.

    :param tree: dict object
    :param validateids: list of TaxIDs or Path to file with TaxIDs to validate
    :return: boolean
    """

    if type(validateids) is list:
        taxids_validate = validateids
    elif type(validateids) is str:
        taxids_validate = parse_tax_ids(validateids)

    taxids_valid = []
    for tax_id in taxids_validate:
        if tax_id in tree:
            taxids_valid.append(True)
        else:
            taxids_valid.append(False)
    return False if False in taxids_valid else True


class TaxonResolver(object):
    def __init__(self, logging=None, **kwargs):
        self.tree = None
        self.logging = logging
        self.kwargs = kwargs

    def download(self, outputfile, outputformat) -> None:
        """Download the NCBI Taxonomy dump file."""
        outputformat = outputformat.lower()
        download_taxonomy_dump(outputfile, outputformat)

    def build(self, inputfile) -> None:
        """Build a tree object from the NCBI Taxonomy dump file."""
        self.tree = build_tree(inputfile)

    def write(self, outputfile, outputformat) -> None:
        """Write a tree object in Pickle format."""
        outputformat = outputformat.lower()
        if outputformat == "pickle":
            write_tree(self.tree, outputfile)
        else:
            if self.logging:
                self.logging(f"Output format '{outputformat}' is not valid!")

    def load(self, inputfile, inputformat) -> None:
        """Load a tree from a Pickle file."""
        inputformat = inputformat.lower()
        if inputformat == "pickle":
            self.tree = load_tree(inputfile)
        else:
            if self.logging:
                self.logging(f"Input format '{inputformat}' is not valid!")

    def validate(self, taxidvalidate) -> bool:
        """Validate a list of TaxIDs against a Tree."""
        return validate_taxids(self.tree, taxidvalidate)

    def search(self, taxidsearch, taxidfilter=None, **kwargs) -> list or None:
        """Search a Tree based on a list of TaxIDs."""
        if validate_taxids(self.tree, taxidsearch):
            return search_taxids(self.tree, taxidsearch, taxidfilter, **kwargs)
        else:
            message = ("Some of the provided TaxIDs are not valid or not found "
                       "in the built Tree.")
            if self.logging:
                logging.warning(message)
            else:
                print_and_exit(message)
