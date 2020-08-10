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

import json
import copy
import pickle
import logging

from anytree import Node

try:
    import fastcache
    from anytree.cachedsearch import find
    from anytree.cachedsearch import findall
except ModuleNotFoundError:
    from anytree.search import find
    from anytree.search import findall

from taxonresolver import TaxonResolver
from taxonresolver.utils import parse_tax_ids
from taxonresolver.utils import print_and_exit


def tree_reparenting(tree_dict: dict) -> dict:
    """
    Loops over the Tree dictionary and reparents every node

    :param tree_dict: dict of anytree node objects
    :return: updated dict object
    """
    for k, v in tree_dict["nodes"].items():
        if v["parent_tax_id"] not in tree_dict["parents"]:
            tree_dict["parents"][v["parent_tax_id"]] = [v["tax_id"]]
        else:
            tree_dict["parents"][v["parent_tax_id"]].append(v["tax_id"])

    return tree_dict


def build_tree(tree: Node) -> dict:
    """
    Given the path to a anytree Tree, builds a slim data structure.

    :param tree: anytree Node object
    :return: dict object
    """

    tree_dict = {"nodes": {}, "parents": {}}
    # read nodes
    for node in findall(tree):
        dict_node = {}
        dict_node["tax_id"] = node.name
        dict_node["parent_tax_id"] = node.parentTaxId
        dict_node["rank"] = node.rank
        tree_dict["nodes"][node.name] = dict_node
    return tree_reparenting(tree_dict)


def load_tree(inputfile: str, inputformat: str = "pickle", **kwargs) -> Node:
    """
    Loads pre-existing Tree from file.

    :param inputfile: Path to outputfile
    :param inputformat: "json" or "pickle"
    :return: dict of anytree node objects
    """

    if inputformat == "pickle":
        return pickle.load(open(inputfile, "rb"))
    elif inputformat == "json":
        with open(inputfile) as data:
            return json.load(data, **kwargs)


def write_tree(tree: Node, outputfile: str, outputformat: str, **kwargs) -> None:
    """
    Writes Tree to file.

    :param tree: anytree Node object
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


def search_tree(tree: dict, taxidfile: str, filterfile: str or None = None,
                sep: str = None, indx: int = 0) -> list:
    """
    Searches an existing Tree and produces a list of TaxIDs.
    Checks if TaxID is in the list, if so provides as is, else,
        searches all children in the list that compose that node.

    :param tree: dict object
    :param taxidfile: Path to file with TaxIDs to search with
    :param filterfile: Path to inputfile, which is a list of
        Taxonomy Identifiers (optional)
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: list of TaxIDs
    """

    taxids_search = parse_tax_ids(taxidfile)
    taxids_filter = []
    if filterfile:
        taxids_filter = parse_tax_ids(filterfile, sep, indx)

    taxids_found = [tax_id for tax_id in taxids_search if tax_id in taxids_filter]
    for tax_id in taxids_search:
        # list of children
        def get_leaves(taxids: list, tree: dict):
            taxids_found.extend(taxids)
            for taxid in taxids:
                try:
                    get_leaves(tree["parents"][taxid], tree)
                except KeyError:
                    # taxid is a leaf node - i.e. it is not a parent of any other TaxID
                    pass

        get_leaves(tree["parents"][tax_id], tree)

    return list(set(taxids_found))


def search_tree_by_taxid(tree: dict, tax_id: str) -> Node:
    """
    Simply checks if TaxID is in the list or in the Tree.

    :param tree: anytree Node object
    :param tax_id: TaxID
    :return: dict object
    """
    return tree["nodes"][tax_id]


def validate_tree(tree: dict, taxidfile: str, inputfile: str or None = None,
                  sep: str = None, indx: int = 0) -> bool:
    """
    Simply checks if TaxID is in the list or in the Tree.

    :param tree: dict object
    :param taxidfile: Path to file with TaxIDs to search with
    :param inputfile: Path to inputfile, which is a list of
        Taxonomy Identifiers
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: boolean
    """

    taxids_search = parse_tax_ids(taxidfile)
    taxids_filter = []
    if inputfile:
        taxids_filter = parse_tax_ids(inputfile, sep, indx)

    taxids_valid = []
    for tax_id in taxids_search:
        if tax_id in taxids_filter or tax_id in tree["nodes"]:
            taxids_valid.append(True)
        else:
            print(tax_id)
            taxids_valid.append(False)
    return False if False in taxids_valid else True


def validate_tree_by_taxid(tree: dict, tax_id: str) -> bool:
    """
    Simply checks if TaxID is in the list or in the Tree.

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

    def build(self, inputfile, inputformat) -> None:
        """Build a tree from NCBI dump file."""
        resolver = TaxonResolver(self.logging)
        resolver.load(inputfile, inputformat)
        self.tree = build_tree(resolver.tree)
        # keep a copy of the original (full) tree
        self._full_tree = copy.copy(self.tree)

    def load(self, inputfile, inputformat) -> None:
        """Load a tree from JSON or Pickle files."""
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

    def validate(self, taxidsearch, taxidfilter=None, **kwargs) -> bool:
        """Validate a list of TaxIDs against a Tree."""
        return validate_tree(self.tree, taxidsearch, taxidfilter, **kwargs)

    def validate_by_taxid(self, taxid) -> bool:
        """Validate a TaxIDs against a Tree."""
        return validate_tree_by_taxid(self.tree, taxid)

    def search(self, taxidsearch, taxidfilter=None, **kwargs) -> list or None:
        """Search a Tree based on a list of TaxIds."""
        if validate_tree(self.tree, taxidsearch, taxidfilter):
            return search_tree(self.tree, taxidsearch, taxidfilter, **kwargs)
        else:
            message = ("Some of the provided TaxIDs are not valid or not found "
                       "in the built Tree.")
            if self.logging:
                logging.warning(message)
            else:
                print_and_exit(message)

    def search_by_taxid(self, taxid) -> Node or None:
        """Retrieve a node by its unique TaxID."""

        if validate_tree_by_taxid(self.tree, taxid):
            return search_tree_by_taxid(self.tree, taxid)
        else:
            message = ("The provided TaxIDs is not valid or not found "
                       "in the built Tree.")
            if self.logging:
                logging.warning(message)
            else:
                print_and_exit(message)
