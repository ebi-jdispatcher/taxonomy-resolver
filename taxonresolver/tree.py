#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import io
import json
import copy
import pickle
import zipfile
import logging
from collections import defaultdict

from anytree import Node
from anytree.importer import JsonImporter
from anytree.exporter import JsonExporter

from taxonresolver.utils import label_to_id
from taxonresolver.utils import escape_literal
from taxonresolver.utils import split_line
from taxonresolver.utils import download_taxonomy_dump
from taxonresolver.library import ncbi_ranks
from taxonresolver.library import ncbi_node_fields


def get_node_from_dict(node: dict) -> Node:
    """
    Given a node dictionary and a label string, return an anytree Node
    representing this tax_id.

    :param node: (defaultdict) node dictionary
    :return: anyTree Node object
    """
    return Node(node["tax_id"],
                rank=node["rank"],
                taxonName=node["label"],
                parentTaxId=node["parent_tax_id"])


def build_tree(inputfile: str, logging: logging = None) -> dict:
    """
    Given the path to the taxdmp.zip file, build a full tree,
    by converting nodes to anytree nodes.

    :param inputfile: Path to taxdmp.zip file
    :param logging: logging obj
    :return: dict of anytree Node objects
    """

    taxon_nodes = defaultdict(list)
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
            logging.debug(f"WARN Unrecognized rank '{rank}'")

        logging.info("Building tree. This may take a few minutes...")
        # If we knew the input file was ordered, we could speed this up massively
        # Loop over has keys and build a tree by reparenting
        for anytree_node in taxon_nodes.values():
            if (anytree_node.parentTaxId and
                    anytree_node.parentTaxId != "" and
                    anytree_node.parentTaxId == anytree_node.name):
                logging.debug(f"Found root for {anytree_node.name}")
            else:
                parent = anytree_node.parentTaxId
                if parent in taxon_nodes:
                    anytree_node.parent = taxon_nodes[parent]
                else:
                    logging.debug(f"No parent found for {anytree_node.name}")

    return taxon_nodes


def load_tree(inputfile: str, inputformat: str = "json", **kwargs):
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
            return importer.import_(json.load(data))


def write_tree(tree_dict: dict, node: str,
               outputfile: str, outputformat: str, **kwargs):
    """
    Writes Tree to file.

    :param tree_dict: dict of anytree node objects
    :param node: node label/name
    :param outputfile: Path to outputfile
    :param outputformat: "json" or "pickle"
    :return: (side-effects) writes to file
    """

    if outputformat == "pickle":
        with open(outputfile, 'wb') as outfile:
            pickle.dump(tree_dict[node], outfile)
    elif outputformat == "json":
        exporter = JsonExporter(indent=2, **kwargs)
        with open(outputfile, "w") as outfile:
            print(exporter.write(tree_dict[node], outfile))


def filter_tree(tree_dict: dict, inputfile: str,
                sep: str = " ", indx: int = 1) -> dict:
    """
    Writes Tree to file.

    :param tree_dict: dict of anytree node objects
    :param inputfile: Path to inputfile, which is a list of
        Taxonomy Identifiers
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: dict of anytree node objects
    """
    taxon_nodes = defaultdict(list)
    tax_ids = []
    with open(inputfile, "r") as infile:
        for line in infile:
            line = line.rstrip()
            tax_id = line.split(sep)[indx]
            tax_ids.append(tax_id)

    # get list of all required (and unique) tax_id parents
    tax_id_parents = []
    for anytree_node in tree_dict.values():
        if anytree_node.name in tax_ids:
            # get full path and use it to capture all
            # levels in the hierarchy that are required
            node_path = anytree_node.path[-1]
            anytree_separator = "/"
            for tax_id in node_path.split(anytree_separator)[1:]:
                tax_id_parents.append(tax_id)

    tax_id_parents = list(set(tax_id_parents))
    for tax_id in tax_id_parents:
        taxon_nodes[tax_id] = tree_dict[tax_id]

    return taxon_nodes


class TaxonResolver(object):
    def __init__(self, logging=None, **kwargs):
        self.tree = None
        self._full_tree = None
        self.node = "root"
        self.logging = logging
        self.kwargs = kwargs
        self._valid_formats = ("json", "pickle")

    def download(self, outputfile, outputformat):
        """Download NCBI Taxonomy dump file"""
        download_taxonomy_dump(outputfile, outputformat)

    def build(self, inputfile):
        """Build tree from NCBI dump file."""
        self.tree = build_tree(inputfile, self.logging)

    def load(self, inputfile, inputformat):
        """Load tree from JSON or Pickle files."""
        if inputformat in self._valid_formats:
            self.tree = load_tree(inputfile, inputformat, **self.kwargs)
        else:
            if self.logging:
                self.logging(f"Input format '{inputformat}' is not valid!")

    def write(self, outputfile, outputformat, node="root"):
        """Write tree in JSON or Pickle formats."""
        if outputformat in self._valid_formats:
            self.node = node
            if self.node == "root":
                self.node = "1"
            write_tree(self.tree, self.node,
                       outputfile, outputformat, **self.kwargs)
        else:
            if self.logging:
                self.logging(f"Output format '{outputformat}' is not valid!")

    def filter(self, inputfile):
        """Re-build tree ignoring Taxonomy IDs provided."""
        # keep a copy of the original (full) tree
        self._full_tree = copy.copy(self.tree)
        if not self._full_tree:
            message = ("The Taxonomy Tree needs to be built "
                       "before 'filter' can be called.")
            if self.logging:
                logging.warning(message)
            else:
                print(message)
        self.tree = filter_tree(self._full_tree, inputfile)

    # TODO
    def search(self):
        pass
