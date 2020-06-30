#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
import pytest
from anytree.search import findall, find_by_attr
from anytree.iterators import PreOrderIter, LevelOrderIter
from taxonresolver import TaxonResolver
from taxonresolver.utils import load_logging


@pytest.fixture
def context():
    return load_logging("INFO")


class TestTree:
    def test_resolver_build(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.build("../testdata/taxdump.zip")
        nodes = findall(resolver.tree)
        assert len(nodes) == 12086
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 8100
        nodes = [node.name for node in PreOrderIter(resolver.tree)]
        assert len(nodes) == 12086
        nodes = [node.name for node in LevelOrderIter(resolver.tree)]
        assert len(nodes) == 12086
        human = find_by_attr(resolver.tree, "9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_build_and_write(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.build("../testdata/taxdump.zip")
        resolver.write("../testdata/tree.pickle", "pickle")
        assert os.path.isfile("../testdata/tree.pickle")
        resolver.write("../testdata/tree.json", "json")
        assert os.path.isfile("../testdata/tree.json")

    def test_resolver_load_pickle(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree.pickle", "pickle")
        nodes = findall(resolver.tree)
        assert len(nodes) == 12086
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 8100

    def test_resolver_load_json(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree.json", "json")
        nodes = findall(resolver.tree)
        assert len(nodes) == 12086
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 8100

    def test_resolver_write_and_load(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree.pickle", "pickle")
        resolver.write("../testdata/tree.json", "json")
        assert os.path.isfile("../testdata/tree.json")

        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree.json", "json")
        nodes = findall(resolver.tree)
        assert len(nodes) == 12086
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 8100
        nodes = [node.name for node in PreOrderIter(resolver.tree)]
        assert len(nodes) == 12086
        nodes = [node.name for node in LevelOrderIter(resolver.tree)]
        assert len(nodes) == 12086
        human = find_by_attr(resolver.tree, "9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_filter(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree.pickle", "pickle")
        resolver.filter("../testdata/taxids_filter.txt")
        nodes = findall(resolver.tree)
        assert len(nodes) == 778
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 593
        nodes = [node.name for node in PreOrderIter(resolver.tree)]
        assert len(nodes) == 778
        nodes = [node.name for node in LevelOrderIter(resolver.tree)]
        assert len(nodes) == 778
        human = find_by_attr(resolver.tree, "9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_filter_and_write(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree.pickle", "pickle")
        resolver.filter("../testdata/taxids_filter.txt")
        resolver.write("../testdata/tree_filtered.pickle", "pickle")
        assert os.path.isfile("../testdata/tree_filtered.pickle")
        resolver.write("../testdata/tree_filtered.json", "json")
        assert os.path.isfile("../testdata/tree_filtered.json")

    def test_resolver_filter_load(self, context):
        resolver = TaxonResolver(logging=context)
        resolver.load("../testdata/tree_filtered.json", "json")
        nodes = findall(resolver.tree)
        assert len(nodes) == 778
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 593
        nodes = [node.name for node in PreOrderIter(resolver.tree)]
        assert len(nodes) == 778
        nodes = [node.name for node in LevelOrderIter(resolver.tree)]
        assert len(nodes) == 778
        human = find_by_attr(resolver.tree, "9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_search(self, context):
        resolver = TaxonResolver(logging=context)
        # resolver.load("../testdata/tree_filtered.json", "json")
        resolver.load("../testdata/tree_filtered.pickle", "pickle")
        tax_ids = resolver.search("../testdata/taxids_search.txt",
                                  "../testdata/taxids_filter.txt")
        assert len(tax_ids) == 10

    def test_resolver_validate(self, context):
        resolver = TaxonResolver(logging=context)
        # resolver.load("../testdata/tree_filtered.json", "json")
        resolver.load("../testdata/tree_filtered.pickle", "pickle")
        assert resolver.validate("../testdata/taxids_validate.txt",
                                 "../testdata/taxids_filter.txt")

    def test_resolver_validate_alt(self, context):
        resolver = TaxonResolver(logging=context)
        # resolver.load("../testdata/tree_filtered.json", "json")
        resolver.load("../testdata/tree_filtered.pickle", "pickle")
        assert not resolver.validate("../testdata/taxids_validate_alt.txt",
                                     "../testdata/taxids_filter.txt")
