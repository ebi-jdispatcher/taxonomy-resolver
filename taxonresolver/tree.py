#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import io
import copy
import pickle
import zipfile
import logging
from collections import defaultdict

from anytree import Node
from anytree.importer import JsonImporter
from anytree.exporter import JsonExporter
from anytree.search import findall
from anytree.search import findall_by_attr

from taxonresolver.utils import label_to_id
from taxonresolver.utils import escape_literal
from taxonresolver.utils import split_line
from taxonresolver.utils import download_taxonomy_dump
from taxonresolver.library import ncbi_ranks
from taxonresolver.library import ncbi_node_fields


def get_node_from_dict(node: dict,
                       named_keys: tuple = ("tax_id", "rank", "label", "parent_tax_id")) -> Node:
    """
    Given a node dictionary and a label string, return an anytree Node
    representing this tax_id.

    :param node: node dict
    :param named_keys: keys to use to create the node
    :return: anytree Node object
    """
    return Node(node[named_keys[0]],
                rank=node[named_keys[1]],
                taxonName=node[named_keys[2]],
                parentTaxId=node[named_keys[3]])


def get_anytree_taxon_nodes(tree, filter_=None):
    """
    Creates a dict of nodes on the fly that is then used for reparenting.

    :param tree: anytree Node object
    :param filter_: function called with every `node` as argument,
        `node` is returned if `True`.
    :return: dict of anytree objects
    """

    taxon_nodes = {}
    keys = ('name', 'rank', 'taxonName', 'parentTaxId')
    for node in findall(tree, filter_=filter_):
        anytree_node = get_node_from_dict({k: v for k, v in node.__dict__.items() if k in keys},
                                          named_keys=keys)
        taxon_nodes[node.name] = anytree_node
    return taxon_nodes


def tree_reparenting(tree_dict: dict, logging: logging or None = None) -> Node:
    """
    Loops over the Tree dictionary and reparents every node

    :param tree_dict: dict of anytree node objects
    :param logging: logging obj
    :return: anytree Node object
    """

    # If we knew the input file was ordered, we could speed this up massively
    # Loop over has keys and build a tree by re-parenting
    def getRONode(tree_dict, tax_id):
        parent_id = tree_dict[tax_id].parentTaxId
        if parent_id in tree_dict:
            if parent_id != tax_id:
                tree_dict[tax_id].parent = tree_dict[parent_id]
                getRONode(tree_dict, parent_id)
            else:
                if logging:
                    logging.debug(f"Found root for {anytree_node.name}")

    for anytree_node in tree_dict.values():
        getRONode(tree_dict, anytree_node.name)
    return tree_dict["1"]


def build_tree(inputfile: str, logging: logging or None = None) -> Node:
    """
    Given the path to the taxdmp.zip file, build a full tree,
    by converting nodes to anytree nodes.

    :param inputfile: Path to taxdmp.zip file
    :param logging: logging obj or None
    :return: anytree Node object
    """

    taxon_nodes = {}
    scientific_names = defaultdict(list)
    labels = {}

    with zipfile.ZipFile(inputfile) as taxdmp:
        # read names
        with taxdmp.open("names.dmp") as dmp:
            for line in io.TextIOWrapper(dmp):
                tax_id, name, unique, name_class, _ = split_line(line)
                if name_class == "scientific name":
                    labels[tax_id] = name
                    scientific_names[name].append([tax_id, unique])

        # use unique name only if there's a conflict
        for name, values in scientific_names.items():
            tax_ids = [x[0] for x in values]
            if len(tax_ids) > 1:
                uniques = [x[1] for x in values]
                if len(tax_ids) != len(set(uniques)):
                    if logging:
                        logging.info("Duplicate unique names", tax_ids, uniques)
                for tax_id, unique in values:
                    labels[tax_id] = unique

        # read nodes
        unrec_ranks = []
        with taxdmp.open("nodes.dmp") as dmp:
            for line in io.TextIOWrapper(dmp):
                dict_node = {}
                fields = split_line(line)
                for i in range(0, min(len(fields), len(ncbi_node_fields))):
                    dict_node[ncbi_node_fields[i]] = fields[i]

                tax_id = dict_node["tax_id"]
                dict_node["label"] = escape_literal(labels[tax_id])
                rank = dict_node["rank"]
                if rank and rank != "" and rank != "no rank":
                    if rank not in ncbi_ranks:
                        unrec_ranks.append(rank)
                    dict_node["rank"] = label_to_id(rank)

                anytree_node = get_node_from_dict(dict_node)
                taxon_nodes[tax_id] = anytree_node

        # any unrecognised ranks?
        for rank in list(set(unrec_ranks)):
            if logging:
                logging.debug(f"WARN Unrecognized rank '{rank}'")

        # tree re-parenting
        root = tree_reparenting(taxon_nodes)
    return root


def load_tree(inputfile: str, inputformat: str = "json", **kwargs) -> Node:
    """
    Loads pre-existing Tree from file.

    :param inputfile: Path to outputfile
    :param inputformat: "json" or "pickle"
    :return: dict of anytree node objects
    """

    if inputformat == "pickle":
        return pickle.load(open(inputfile, "rb"))
    elif inputformat == "json":
        importer = JsonImporter(**kwargs)
        with open(inputfile) as data:
            taxon_nodes = get_anytree_taxon_nodes(importer.read(data))
            # tree re-parenting
            return tree_reparenting(taxon_nodes)


def write_tree(tree: Node, outputfile: str, outputformat: str, **kwargs) -> None:
    """
    Writes Tree to file.

    :param tree: anytree Node object
    :param outputfile: Path to outputfile
    :param outputformat: "json" or "pickle"
    :return: (side-effects) writes to file
    """

    if outputformat == "pickle":
        with open(outputfile, 'wb') as outfile:
            pickle.dump(tree, outfile)
    elif outputformat == "json":
        exporter = JsonExporter(**kwargs)
        with open(outputfile, "w") as outfile:
            exporter.write(tree, outfile)


def filter_tree(tree: Node, filterfile: str,
                sep: str = " ", indx: int = 0) -> Node:
    """
    Filters an existing Tree based on a List of TaxIDs file.

    :param tree: anytree Node object
    :param filterfile: Path to inputfile, which is a list of
        Taxonomy Identifiers
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: anytree Node object
    """

    tax_ids = []
    with open(filterfile, "r") as infile:
        for line in infile:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            tax_id = line.split(sep)[indx]
            tax_ids.append(tax_id)

    # get list of all required (and unique) tax_id parents
    tax_id_parents = []
    for tax_id in tax_ids:
        # get full path and use it to capture all
        # levels in the hierarchy that are required
        node = findall_by_attr(tree, tax_id)
        for tax_id in str(node).split("'")[1].split("/")[1:]:
            tax_id_parents.append(tax_id)

    tax_id_parents = list(set(tax_id_parents))
    taxon_nodes = get_anytree_taxon_nodes(tree, filter_=lambda n: n.name in tax_id_parents)
    # tree re-parenting
    root = tree_reparenting(taxon_nodes)
    return root


def search_tree(tree: Node, taxidfile: str, filterfile: str or None = None,
                sep: str = " ", indx: int = 0) -> list:
    """
    Searches an existing Tree and produces a list of TaxIDs.
    Checks if TaxID is in the list, if so provides as is, else,
        searches all children in the list that compose that node.

    :param tree: anytree Node object
    :param taxidfile: Path to file with TaxIDs to search with
    :param filterfile: Path to inputfile, which is a list of
        Taxonomy Identifiers (optional)
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: list of TaxIDs
    """

    taxids_search = []
    with open(taxidfile, "r") as infile:
        for line in infile:
            if line.startswith("#"):
                continue
            tax_id = line.rstrip()
            taxids_search.append(tax_id)

    taxids_filter = []
    if filterfile:
        with open(filterfile, "r") as infile:
            for line in infile:
                if line.startswith("#"):
                    continue
                line = line.rstrip()
                tax_id = line.split(sep)[indx]
                taxids_filter.append(tax_id)

    taxids_found = [tax_id for tax_id in taxids_search if tax_id in taxids_filter]
    allsps = findall(tree, filter_=lambda n: n.rank == "species")
    allsps_paths = [str(node.path[-1]).split("'")[1] for node in allsps]
    for node in findall(tree, filter_=lambda n: n.name in taxids_search):
        for sppath in allsps_paths:
            if node.name in sppath:
                taxids_found.extend(sppath.split("/")[-1])
    return list(set(taxids_found))


def validate_tree(tree: Node, taxidfile: str, inputfile: str or None = None,
                  sep: str = " ", indx: int = 0) -> bool:
    """
    Simply checks if TaxID is in the list or in the Tree.

    :param tree: anytree Node object
    :param taxidfile: Path to file with TaxIDs to search with
    :param inputfile: Path to inputfile, which is a list of
        Taxonomy Identifiers
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: boolean
    """

    taxids_search = []
    with open(taxidfile, "r") as infile:
        for line in infile:
            if line.startswith("#"):
                continue
            tax_id = line.rstrip()
            taxids_search.append(tax_id)

    taxids_filter = []
    if inputfile:
        with open(inputfile, "r") as infile:
            for line in infile:
                if line.startswith("#"):
                    continue
                line = line.rstrip()
                tax_id = line.split(sep)[indx]
                taxids_filter.append(tax_id)

    taxids_valid = []
    for tax_id in taxids_search:
        if (tax_id in taxids_filter or
                tax_id in [node.name for node in findall_by_attr(tree, tax_id)]):
            taxids_valid.append(True)
        else:
            taxids_valid.append(False)
    return False if False in taxids_valid else True


class TaxonResolver(object):
    def __init__(self, logging=None, **kwargs):
        self.tree = None
        self._full_tree = None
        self.logging = logging
        self.kwargs = kwargs
        self._valid_formats = ("json", "pickle")

    def download(self, outputfile, outputformat):
        """Download NCBI Taxonomy dump file."""
        outputformat = outputformat.lower()
        download_taxonomy_dump(outputfile, outputformat)

    def build(self, inputfile):
        """Build a tree from NCBI dump file."""
        self.tree = build_tree(inputfile, self.logging)

    def load(self, inputfile, inputformat):
        """Load a tree from JSON or Pickle files."""
        inputformat = inputformat.lower()
        if inputformat in self._valid_formats:
            self.tree = load_tree(inputfile, inputformat, **self.kwargs)
        else:
            if self.logging:
                self.logging(f"Input format '{inputformat}' is not valid!")

    def write(self, outputfile, outputformat):
        """Write a tree in JSON or Pickle formats."""
        outputformat = outputformat.lower()
        if outputformat in self._valid_formats:
            write_tree(self.tree, outputfile, outputformat, **self.kwargs)
        else:
            if self.logging:
                self.logging(f"Output format '{outputformat}' is not valid!")

    def filter(self, taxidfilter):
        """Re-build a tree ignoring Taxonomy IDs provided."""
        # keep a copy of the original (full) tree
        self._full_tree = copy.copy(self.tree)
        if not self._full_tree:
            message = ("The Taxonomy Tree needs to be built "
                       "before 'filter' can be called.")
            if self.logging:
                logging.warning(message)
            else:
                print(message)
        self.tree = filter_tree(self.tree, taxidfilter)

    def search(self, taxidsearch, taxidfilter=None):
        """Search a Tree based on a list of TaxIds."""
        return search_tree(self.tree, taxidsearch, taxidfilter)

    def validate(self, taxidsearch, taxidfilter=None):
        """Validate a list of TaxIDs agains a Tree."""
        return validate_tree(self.tree, taxidsearch, taxidfilter)
