#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2024.
:license: Apache 2.0, see LICENSE for more details.
"""

import logging
import os
import sys

import pandas as pd
import requests


def get_logging_level(level: str = "INFO") -> logging:
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARN":
        return logging.WARN
    elif level == "ERROR":
        return logging.ERROR
    elif level == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO


def load_logging(
    log_level: str, log_output: str = None, disabled: bool = False
) -> logging:
    logging.basicConfig(
        format="%(asctime)s - [%(levelname)s] %(message)s",
        level=get_logging_level(log_level),
        datefmt="%d/%m/%Y %H:%M:%S",
    )
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


def validate_inputs_outputs(
    inputfile: str or None = None, outputfile: str or None = None
) -> None:
    """
    Checks if the passed input/output files are valid and exist.

    :param inputfile: input file paths
    :param outputfile: output file paths
    :return: (side-effects)
    """

    if inputfile:
        if not os.path.isfile(inputfile):
            print_and_exit(
                f"Input file '{inputfile}' does not exist or it is not readable!"
            )

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
        open(outfile, "wb").write(r.content)
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

    taxids = []
    with open(inputfile, "r") as infile:
        for line in infile:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            if line != "":
                if sep:
                    taxid = line.split(sep)[indx]
                else:
                    taxid = line.split()[indx]
                if taxid != "":
                    taxids.append(taxid)
    return taxids


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


def tree_traversal(node: dict or list, nodes: list, depth: int = 1) -> list:
    """
    Iterate over tree using pre-order strategy. Returns a list of all nodes
    visited in order (nodes and depths).

    :param node: dict object
    :param nodes: list of TaxIDs
    :param depth: tree depth
    :return: list of tuples
    """

    if isinstance(node, dict):
        nodes.append((node["id"], depth))
        if "children" in node.keys():
            depth += 1
            tree_traversal(node["children"], nodes, depth)
            depth -= 1
            nodes.append((node["id"], depth))
        else:
            nodes.append((node["id"], depth))
    elif isinstance(node, list):
        for d in node:
            tree_traversal(d, nodes, depth)
    return nodes


def get_nested_sets(tree: pd.DataFrame) -> list:
    """
    Get only lft and rgt values that make larger nested sets,
    i.e. smaller containers (sub-trees) that are already part of larger
    containers are dropped, to reduce number of table operations

    :param tree: pandas DataFrame
    :return: list of tuples
    """
    nested_sets = []
    tmp_lft, tmp_rgt = 0, 0
    for l, r in zip(tree["lft"].values, tree["rgt"].values):
        if l > tmp_lft and r > tmp_rgt:
            tmp_lft, tmp_rgt = l, r
            nested_sets.append((l, r))
    return nested_sets


def get_children(tree: pd.DataFrame, lft: int, rgt: int) -> list:
    """
    Subsets the DataFrame to find all children TaxIDs from a particular node.

    :param tree: pandas DataFrame
    :param lft: left index based on MPTT
    :param rgt: right index based on MPTT
    :return: list of TaxIDs
    """
    return tree[(tree["lft"] > lft) & (tree["rgt"] < rgt)]["id"].values


def get_parents(tree: pd.DataFrame, lft: int, rgt: int) -> list:
    """
    Subsets the DataFrame to find all parent TaxIDs from a particular node.

    :param tree: pandas DataFrame
    :param lft: left index based on MPTT
    :param rgt: right index based on MPTT
    :return: list of TaxIDs
    """
    return tree[(tree["lft"] < lft) & (tree["rgt"] > rgt)]["id"].values
