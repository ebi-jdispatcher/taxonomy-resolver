#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

"""
Used for testing a fast search and validation.
It is not intended for building and filtering, which is performed
by the main tree.py.
"""

import io
import json
import copy
import pickle
import zipfile
import logging

from anytree import Node

try:
    import fastcache
    from anytree.cachedsearch import find
    from anytree.cachedsearch import findall
except ModuleNotFoundError:
    from anytree.search import find
    from anytree.search import findall

from taxonresolver.utils import parse_tax_ids
from taxonresolver.utils import print_and_exit
from taxonresolver.utils import split_line
from taxonresolver.utils import label_to_id


def tree_reparenting(tree_dict: dict) -> dict:
    """
    Loops over the Tree dictionary and re-parents every node.

    :param tree_dict: dict of anytree node objects
    :return: updated dict object
    """
    for k, v in tree_dict["nodes"].items():
        if v["parent_tax_id"] not in tree_dict["children"]:
            tree_dict["children"][v["parent_tax_id"]] = [v["tax_id"]]
        else:
            tree_dict["children"][v["parent_tax_id"]].append(v["tax_id"])

    return tree_dict


def build_tree(inputfile: str) -> dict:
    """
    Given the path to a anytree Tree, builds a slim data structure.

    :param tree: anytree Node object
    :return: dict object
    """

    tree_dict = {"nodes": {}, "children": {}}
    # read nodes
    with zipfile.ZipFile(inputfile) as taxdmp:
        with taxdmp.open("nodes.dmp") as dmp:
            for line in io.TextIOWrapper(dmp):
                dict_node = {}
                fields = split_line(line)
                dict_node["tax_id"] = fields[0]
                dict_node["parent_tax_id"] = fields[1]
                dict_node["rank"] = label_to_id(fields[2])
                tree_dict["nodes"][dict_node["tax_id"]] = dict_node
    return tree_reparenting(tree_dict)


def load_tree(inputfile: str, inputformat: str = "pickle", **kwargs) -> Node:
    """
    Loads a pre-existing Tree from file.

    :param inputfile: Path to outputfile
    :param inputformat: "json" or "pickle"
    :return: dict object
    """

    if inputformat == "pickle":
        return pickle.load(open(inputfile, "rb"))
    elif inputformat == "json":
        with open(inputfile) as data:
            return json.load(data, **kwargs)


def write_tree(tree: dict, outputfile: str, outputformat: str, **kwargs) -> None:
    """
    Writes a Tree to file.

    :param tree: dict object
    :param outputfile: Path to outputfile
    :param outputformat: "json" or "pickle"
    :return: (side-effects) writes to file
    """

    if outputformat == "pickle" or outputformat == "fast":
        with open(outputfile, 'wb') as outfile:
            pickle.dump(tree, outfile)
    elif outputformat == "json":
        with open(outputfile, 'w') as outfile:
            json.dump(tree, outfile, **kwargs)


def filter_tree(tree: dict, filterids: list or str,
                sep: str = None, indx: int = 0) -> dict:
    """
    Filters an existing Tree based on a list of TaxIDs.

    :param tree: fast dict object
    :param filterids: list of TaxIDs or Path to inputfile,
        which is a list of TaxIDs
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: dict object
    """
    tax_ids = []
    if type(filterids) is list:
        tax_ids = filterids
    elif type(filterids) is str:
        tax_ids = parse_tax_ids(filterids, sep, indx)

    # skipping "invalid" ids
    tax_ids = [tax_id for tax_id in tax_ids if validate_by_taxid(tree, tax_id)]

    # get list of all required (and unique) parents and children taxIDs
    tree_dict = {"nodes": {}, "children": {}}
    for tax_id in tax_ids:
        tree_dict["nodes"][tax_id] = tree["nodes"][tax_id]

    return tree_reparenting(tree_dict)


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
    taxids_found = []
    for tax_id in taxids_search:
        # list of children
        def get_leaves(taxids: list, tree: dict):
            taxids_found.extend(taxids)
            for taxid in taxids:
                try:
                    get_leaves(tree["children"][taxid], tree)
                except KeyError:
                    # taxid is a leaf node - i.e. it is not a parent of any other TaxID
                    pass

        if tax_id in tree["children"]:
            get_leaves(tree["children"][tax_id], tree)

    taxids_filter = []
    if type(filterids) is list:
        taxids_filter = filterids
    elif type(filterids) is str:
        taxids_filter = parse_tax_ids(filterids, sep, indx)
    if taxids_filter:
        taxids_found = [tax_id for tax_id in taxids_found if tax_id in taxids_filter]
    return list(set(taxids_found))


def find_by_taxid(tree: dict, tax_id: str) -> Node:
    """
    Retrieves a TaxID dict.

    :param tree: anytree Node object
    :param tax_id: TaxID
    :return: dict object
    """
    return tree["nodes"][tax_id]


def validate_taxids(tree: dict, validateids: list or str or None,
                    filterids: list or str or None = None,
                    sep: str = None, indx: int = 0) -> bool:
    """
    Checks if TaxIDs are in the list and in the Tree.

    :param tree: dict object
    :param validateids: list of TaxIDs or Path to file with TaxIDs to validate
    :param filterids: list of TaxIDs or None or Path to inputfile,
        which is a list of TaxIDs (optional)
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: boolean
    """

    if type(validateids) is list:
        taxids_validate = validateids
    elif type(validateids) is str:
        taxids_validate = parse_tax_ids(validateids)

    taxids_filter = []
    if type(filterids) is list:
        taxids_filter = filterids
    elif type(filterids) is str:
        taxids_filter = parse_tax_ids(filterids, sep, indx)

    taxids_valid = []
    for tax_id in taxids_validate:
        if tax_id in taxids_filter or tax_id in tree["nodes"]:
            taxids_valid.append(True)
        else:
            taxids_valid.append(False)
    return False if False in taxids_valid else True


def validate_by_taxid(tree: dict, tax_id: str) -> bool:
    """
    Checks if a TaxID is in the Tree.

    :param tree: dict object
    :param tax_id: TaxID
    :return: boolean
    """
    return tax_id in tree["nodes"]


class TaxonResolverFast(object):
    def __init__(self, logging=None, **kwargs):
        self.tree = None
        self._full_tree = None
        self.logging = logging
        self.kwargs = kwargs
        self._valid_formats = ("json", "pickle")

    def build(self, inputfile) -> None:
        """Build a tree from NCBI dump file."""
        self.tree = build_tree(inputfile)
        # keep a copy of the original (full) tree
        self._full_tree = copy.copy(self.tree)

    def load(self, inputfile, inputformat) -> None:
        """Load a tree from JSON or Pickle file."""
        inputformat = inputformat.lower()
        if inputformat in self._valid_formats:
            self.tree = load_tree(inputfile, inputformat, **self.kwargs)
            # keep a copy of the original (full) tree
            self._full_tree = copy.copy(self.tree)
        else:
            if self.logging:
                self.logging(f"Input format '{inputformat}' is not valid!")

    def write(self, outputfile, outputformat) -> None:
        """Write a tree in JSON or Pickle formats."""
        outputformat = outputformat.lower()
        if outputformat in self._valid_formats:
            write_tree(self.tree, outputfile, outputformat, **self.kwargs)
        else:
            if self.logging:
                self.logging(f"Output format '{outputformat}' is not valid!")

    def filter(self, taxidfilter, **kwargs) -> None:
        """Re-build a Tree based on the TaxIDs provided."""
        if not self._full_tree:
            message = ("The Taxonomy Tree needs to be built "
                       "before 'filter' can be called.")
            if self.logging:
                logging.warning(message)
            else:
                print_and_exit(message)
        self.tree = filter_tree(self.tree, taxidfilter, **kwargs)

    def validate(self, taxidvalidate, taxidfilter=None, **kwargs) -> bool:
        """Validate a list of TaxIDs against a Tree."""
        return validate_taxids(self.tree, taxidvalidate, taxidfilter, **kwargs)

    def validate_by_taxid(self, taxid) -> bool:
        """Validate a TaxID against a Tree."""
        return validate_by_taxid(self.tree, taxid)

    def search(self, taxidsearch, taxidfilter=None, **kwargs) -> list or None:
        """Search a Tree based on a list of TaxIDs."""
        if validate_taxids(self.tree, taxidsearch, taxidfilter):
            return search_taxids(self.tree, taxidsearch, taxidfilter, **kwargs)
        else:
            message = ("Some of the provided TaxIDs are not valid or not found "
                       "in the built Tree.")
            if self.logging:
                logging.warning(message)
            else:
                print_and_exit(message)

    def find_by_taxid(self, taxid) -> Node or None:
        """Retrieve a node by its unique TaxID."""

        if validate_by_taxid(self.tree, taxid):
            return find_by_taxid(self.tree, taxid)
        else:
            message = ("The provided TaxIDs is not valid or not found "
                       "in the built Tree.")
            if self.logging:
                logging.warning(message)
            else:
                print_and_exit(message)
