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

from taxonresolver.utils import parse_tax_ids
from taxonresolver.utils import print_and_exit
from taxonresolver.utils import split_line
from taxonresolver.utils import download_taxonomy_dump
from taxonresolver.utils import get_all_children


def tree_reparenting(tree: dict) -> dict:
    """
    Loops over the Tree dictionary and re-parents every node to
    find all the node's children.

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
    Given the path to NCBI Taxonomy 'taxdmp.zip' file or simply a
    'nodes.dmp' file, builds a slim tree data structure.

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


def write_tree(tree: dict, outputfile: str, outputformat: str = "pickle") -> None:
    """
    Writes a tree dict object to file.

    :param tree: dict object
    :param outputfile: Path to outputfile
    :param outputformat: currently "pickle" format
    :return: (side-effects) writes to file
    """
    if outputformat == "pickle":
        with open(outputfile, 'wb') as outfile:
            pickle.dump(tree, outfile)
    else:
        print_and_exit(f"Input format '{outputformat}' is not valid!")


def load_tree(inputfile: str, inputformat: str = "pickle") -> dict:
    """
    Loads a pre-existing tree dict from file.

    :param inputfile: Path to outputfile
    :param inputformat: currently "pickle" format
    :return: dict object
    """
    if inputformat == "pickle":
        return pickle.load(open(inputfile, "rb"))
    else:
        print_and_exit(f"Input format '{inputformat}' is not valid!")


def search_taxids(tree: dict,
                  includeids: list or str,
                  excludeids: list or str or None = None,
                  filterids: list or str or None = None,
                  ignoreinvalid: bool = False,
                  sep: str = None, indx: int = 0) -> list:
    """
    Searches an existing tree dict and produces a list of TaxIDs.
    Search is performed based on a list of TaxIDs (includedids). A search is also
    performed on a list of TaxIDs (excludedids), if provided. Those will be
    removed from the search on the includedids. From this final list of TaxIDs,
    filterids can used to clean the final set. This could be useful to compress a
    final list of TaxIDs, to only return those known to exist in another dataset.

    :param tree: dict object
    :param includeids: list of TaxIDs or Path to file with TaxIDs to search with
    :param excludeids: list of TaxIDs or Path to file with TaxIDs to exclude
        from the search (optional)
    :param filterids: list of TaxIDs or Path to file with TaxIDs to filter
        (i.e. to keep) in the final set of results (optional)
    :param ignoreinvalid: whether to ignore invalid TaxIDs or not
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: list of TaxIDs
    """

    message = ("Some of the provided TaxIDs are not valid or not found "
               "in the built Tree.")

    # find all the children nodes of the list of TaxIDs to be included in the search
    if type(includeids) is list:
        taxids_include = includeids
    elif type(includeids) is str:
        taxids_include = parse_tax_ids(includeids)
    if ignoreinvalid or validate_taxids(tree, taxids_include):
        taxids_found = taxids_include[:]
        for taxid in taxids_include:
            if taxid in tree:
                get_all_children(tree[taxid], taxids_found, taxid)
    else:
        print_and_exit(message)

    # find all the children nodes of the list of TaxIDs to be excluded from the search
    if excludeids:
        if type(excludeids) is list:
            taxids_exclude = excludeids
        elif type(excludeids) is str:
            taxids_exclude = parse_tax_ids(excludeids)
        if ignoreinvalid or validate_taxids(tree, taxids_exclude):
            taxids_excluded = taxids_exclude[:]
            for taxid in taxids_exclude:
                if taxid in tree:
                    get_all_children(tree[taxid], taxids_excluded, taxid)
            taxids_found = [taxid for taxid in taxids_found if taxid not in taxids_excluded]
        else:
            print_and_exit(message)

    # keep only TaxIDs that are in the provided list of TaxIDs to filter with
    if filterids:
        if type(filterids) is list:
            taxids_filter = filterids
        elif type(filterids) is str:
            taxids_filter = parse_tax_ids(filterids, sep, indx)
        if ignoreinvalid or validate_taxids(tree, taxids_filter):
            taxids_found = [tax_id for tax_id in taxids_found if tax_id in taxids_filter]
        else:
            print_and_exit(message)

    return list(set(taxids_found))


def validate_taxids(tree: dict, validateids: list or str) -> bool:
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
        write_tree(self.tree, outputfile, outputformat)

    def load(self, inputfile, inputformat) -> None:
        """Load a tree from a Pickle file."""
        self.tree = load_tree(inputfile, inputformat)

    def validate(self, taxidinclude) -> bool:
        """Validate a list of TaxIDs against a Tree."""
        return validate_taxids(self.tree, taxidinclude)

    def search(self, taxidinclude, taxidexclude=None, taxidfilter=None,
               ignoreinvalid=False, **kwargs) -> list or None:
        """Search a Tree based on a list of TaxIDs."""
        return search_taxids(self.tree, taxidinclude, taxidexclude, taxidfilter,
                             ignoreinvalid, **kwargs)
