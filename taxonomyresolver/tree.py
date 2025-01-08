#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2024.
:license: Apache 2.0, see LICENSE for more details.
"""

import io
import zipfile

import pandas as pd
from tqdm import tqdm

from taxonomyresolver.utils import (
    download_taxonomy_dump,
    get_children,
    get_nested_sets,
    get_parents,
    parse_tax_ids,
    print_and_exit,
    split_line,
    tree_reparenting,
    tree_traversal,
    tree_to_newick,
)


def build_tree(inputfile: str, root: str = "1") -> pd.DataFrame:
    """
    Given the path to NCBI Taxonomy 'taxdmp.zip' file or simply a
    'nodes.dmp' file, builds a slim tree data structure.

    :param inputfile: Path to inputfile
    :param root: TaxID of the root Node
    :return: pandas DataFrame
    """

    tree = {}
    # read nodes
    if zipfile.is_zipfile(inputfile):
        with zipfile.ZipFile(inputfile) as taxdmp:
            dmp = taxdmp.open("nodes.dmp")
    else:
        dmp = open(inputfile, "rb")
    for line in tqdm(
        io.TextIOWrapper(dmp, encoding="unicode_escape"), desc="Reading tree dump"
    ):
        fields = split_line(line)
        tree[fields[0]] = {"id": fields[0], "parent_id": fields[1], "rank": fields[2]}
    dmp.close()
    # creating a full tree
    tree = tree_reparenting(tree)

    # transversing the tree to find 'left' and 'right' indexes
    nodes = []
    tree_traversal(tree[root], nodes)
    nested_set, visited, counter = [], {}, -1
    for i, node in tqdm(enumerate(nodes), total=len(tree), desc="Building tree"):
        taxid, depth = node[0], node[1]
        parent_id, rank = tree[taxid]["parent_id"], tree[taxid]["rank"]
        if taxid not in visited:
            # create array with left ('lft') index
            nested_set.append([taxid, parent_id, rank, depth, i + 1, 0])
            counter += 1
            visited[taxid] = counter
        else:
            # update the right ('rgt') index
            nested_set[visited[taxid]][5] = i + 1

    # load dict into a pandas DataFrame for fast indexing and operations
    df = pd.DataFrame(
        nested_set, columns=["id", "parent_id", "rank", "depth", "lft", "rgt"]
    ).astype(dtype={"id": str, "parent_id": str, "rank": str})
    return df


def write_tree(
    tree: pd.DataFrame | None, outputfile: str, outputformat: str = "pickle"
) -> None:
    """
    Writes a pandas DataFrame object to file.

    :param tree: pandas DataFrame
    :param outputfile: Path to outputfile
    :param outputformat: currently "pickle" or "newick" format
    :return: (side-effects) writes to file
    """
    if outputformat == "pickle" and tree is not None:
        tree.to_pickle(outputfile, protocol=4)
    elif outputformat == "newick" and tree is not None:
        with open(outputfile, "w") as outfile:
            outfile.write(tree_to_newick(tree) + "\n")
    # elif outputformat == "shelve":
    #     with shelve.open(outputfile) as outfile:
    #         outfile["tree"] = tree
    # elif outputformat == "marshal":
    #     with open(outputfile, 'wb') as outfile:
    #         marshal.dump(tree, outfile)
    # elif outputformat == "hdf5":
    #     tree.to_hdf(outputfile, "df")
    else:
        print_and_exit(f"Output format '{outputformat}' is not valid!")


def load_tree(inputfile: str, inputformat: str = "pickle") -> pd.DataFrame | None:
    """
    Loads a pre-existing pandas DataFrame from file.

    :param inputfile: Path to outputfile
    :param inputformat: currently "pickle" format
    :return: pandas DataFrame
    """
    if inputformat == "pickle":
        return pd.read_pickle(inputfile)
    # elif inputformat == "shelve":
    #     with shelve.open(inputfile) as db:
    #         return db["tree"]
    # elif inputformat == "marshal":
    #     return marshal.load(open(inputfile, "rb"))
    # elif inputformat == "hdf5":
    #     return pd.read_hdf(inputfile, "df")
    else:
        print_and_exit(f"Input format '{inputformat}' is not valid!")


def filter_tree(
    tree: pd.DataFrame | None,
    filterids: list | str | None = None,
    root: str = "1",
    ignoreinvalid: bool = True,
    sep: str | None = None,
    indx: int = 0,
) -> pd.DataFrame | None:
    """
    Filters an existing pandas DataFrame based on a List of TaxIDs.

    :param tree: pandas DataFrame
    :param filterids: list of TaxIDs or Path to file with TaxIDs to filter
        (i.e. to keep) in the final set of results (optional)
    :param root: TaxID of the root Node
    :param ignoreinvalid: whether to ignore invalid TaxIDs or not
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the resulting list
    :return: pandas DataFrame
    """

    message = (
        "Some of the provided TaxIDs are not valid or not found in the built Tree."
    )

    taxids_filter = set()
    if type(filterids) is list:
        taxids_filter = set(filterids)
    elif type(filterids) is str:
        taxids_filter = set(parse_tax_ids(filterids, sep, indx))

    if ignoreinvalid or validate_taxids(tree, taxids_filter):
        # if ignoring invalid, we should still only return TaxIDs that exist in the Tree
        if tree is not None:
            taxids_filter = taxids_filter.intersection(set(tree["id"].values))
            # get a subset dataset sorted (by 'lft')
            subset = tree[tree["id"].isin(taxids_filter)].sort_values("lft")
            nested_sets = get_nested_sets(subset)
            for l, r in nested_sets:
                taxids = get_children(tree, l, r)
                taxids_filter.update(taxids)
                # expand taxids_filter with parents of the selected node
                taxids = get_parents(tree, l, r)
                taxids_filter.update(taxids)
            return tree[tree["id"].isin(taxids_filter)].reset_index()
    else:
        print_and_exit(message)


def search_taxids(
    tree: pd.DataFrame | None,
    includeids: list | str,
    excludeids: list | str | None = None,
    filterids: list | str | None = None,
    ignoreinvalid: bool = True,
    sep: str | None = None,
    indx: int = 0,
) -> list | set | None:
    """
    Searches an existing tree pandas DataFrame and produces a list of TaxIDs.
    Search is performed based on a list of TaxIDs (includedids). A search is also
    performed on a list of TaxIDs (excludedids), if provided. Those will be
    removed from the search on the includedids. From this final list of TaxIDs,
    filterids can used to clean the final set. This could be useful to compress a
    final list of TaxIDs, to only return those known to exist in another dataset.

    :param tree: pandas DataFrame
    :param includeids: list of TaxIDs or Path to file with TaxIDs to search with
    :param excludeids: list of TaxIDs or Path to file with TaxIDs to exclude
        from the search (optional)
    :param filterids: list of TaxIDs or Path to file with TaxIDs to filter
        (i.e. to keep) in the final set of results (optional)
    :param ignoreinvalid: whether to ignore invalid TaxIDs or not
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the resulting list
    :return: list of TaxIDs
    """

    message = (
        "Some of the provided TaxIDs are not valid or not found in the built Tree."
    )

    # find all the children nodes of the list of TaxIDs to be included in the search
    taxids_include = set()
    taxids_found = set()
    if type(includeids) is list:
        taxids_include = set(includeids)
    elif type(includeids) is str:
        taxids_include = set(parse_tax_ids(includeids))
    if ignoreinvalid or validate_taxids(tree, taxids_include):
        # if ignoring invalid, we should still only return TaxIDs that exist in the Tree
        if tree is not None:
            taxids_found = taxids_include.intersection(set(tree["id"].values))
            # get a subset dataset sorted (by 'lft')
            subset = tree[tree["id"].isin(taxids_found)].sort_values("lft")
            nested_sets = get_nested_sets(subset)
            for l, r in nested_sets:
                taxids = get_children(tree, l, r)
                taxids_found.update(taxids)
    else:
        print_and_exit(message)

    # find all the children nodes of the list of TaxIDs to be excluded from the search
    if excludeids:
        taxids_exclude = set()
        if type(excludeids) is list:
            taxids_exclude = set(excludeids)
        elif type(excludeids) is str:
            taxids_exclude = set(parse_tax_ids(excludeids))
        if ignoreinvalid or validate_taxids(tree, taxids_exclude):
            if tree is not None:
                subset = tree[tree["id"].isin(taxids_exclude)].sort_values("lft")
                nested_sets = get_nested_sets(subset)
                for l, r in nested_sets:
                    taxids = get_children(tree, l, r)
                    taxids_exclude.update(taxids)
                if taxids_found:
                    taxids_found = taxids_found.difference(taxids_exclude)
        else:
            print_and_exit(message)

    # keep only TaxIDs that are in the provided list of TaxIDs to filter with
    if filterids:
        taxids_filter = set()
        if type(filterids) is list:
            taxids_filter = set(filterids)
        elif type(filterids) is str:
            taxids_filter = set(parse_tax_ids(filterids, sep, indx))
        if ignoreinvalid or validate_taxids(tree, taxids_filter):
            taxids_found = taxids_found.intersection(taxids_filter)
        else:
            print_and_exit(message)
    return taxids_found


def validate_taxids(tree: pd.DataFrame | None, validateids: list | set | str) -> bool:
    """
    Checks if TaxIDs are in the list and in the Tree.

    :param tree: pandas DataFrame
    :param validateids: list of TaxIDs or Path to file with TaxIDs to validate
    :return: boolean
    """
    taxids_validate = set()
    if type(validateids) is list:
        taxids_validate = set(validateids)
    elif type(validateids) is set:
        taxids_validate = validateids
    elif type(validateids) is str:
        taxids_validate = set(parse_tax_ids(validateids))

    if tree is not None:
        taxids_valid = taxids_validate.intersection(set(tree["id"].values))
        if len(taxids_valid) == len(taxids_validate):
            return True
    return False


class TaxonResolver(object):
    def __init__(self, logging=None, **kwargs):
        self.tree = None
        self.logging = logging
        self.kwargs = kwargs

    def download(self, outputfile, outputformat="zip") -> None:
        """Download the NCBI Taxonomy dump file."""
        outputformat = outputformat.lower()
        download_taxonomy_dump(outputfile, outputformat)

    def build(self, inputfile) -> None:
        """Build a Tree from the NCBI Taxonomy dump file."""
        self.tree = build_tree(inputfile)

    def write(self, outputfile, outputformat="pickle") -> None:
        """Write a Tree in Pickle format."""
        write_tree(self.tree, outputfile, outputformat)

    def load(self, inputfile, inputformat="pickle") -> None:
        """Load a Tree from a Pickle file."""
        self.tree = load_tree(inputfile, inputformat)

    def filter(self, taxidfilter, **kwargs) -> None:
        """Re-build a minimal Tree based on the TaxIDs provided."""
        if not type(self.tree) is pd.DataFrame:
            message = (
                "The Taxonomy Tree needs to be built before 'filter' can be called."
            )
            print_and_exit(message)
        self.tree = filter_tree(self.tree, taxidfilter, **kwargs)

    def validate(self, taxidinclude) -> bool:
        """Validate a list of TaxIDs against a Tree."""
        return validate_taxids(self.tree, taxidinclude)

    def search(
        self,
        taxidinclude,
        taxidexclude=None,
        taxidfilter=None,
        ignoreinvalid=True,
        **kwargs,
    ) -> list | set | None:
        """Search a Tree based on a list of TaxIDs."""
        return search_taxids(
            self.tree, taxidinclude, taxidexclude, taxidfilter, ignoreinvalid, **kwargs
        )
