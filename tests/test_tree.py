#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2021.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
import pytest

try:
    import fastcache
    from anytree.cachedsearch import findall
    from anytree.cachedsearch import find_by_attr
except ModuleNotFoundError:
    from anytree.search import findall
    from anytree.search import find_by_attr
from anytree.iterators import PreOrderIter
from anytree.iterators import LevelOrderIter
from taxonresolver import TaxonResolver
from taxonresolver.utils import load_logging


@pytest.fixture
def context():
    return load_logging("INFO")


@pytest.fixture
def cwd():
    if not os.getcwd().endswith("tests"):
        os.chdir(os.path.join(os.getcwd(), "tests"))
    return os.getcwd()


class TestTree:
    @pytest.mark.skip(reason="Skip test by default!")
    def test_download_taxdump(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.download(os.path.join(cwd, f"../testdata/taxdump_full.zip"), "zip")
        assert os.path.isfile(os.path.join(cwd, "../testdata/taxdump_full.zip"))

    def test_resolver_build(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdump.zip"))
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
        human = resolver.find_by_taxid("9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_build_and_write(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdump.zip"))
        resolver.write(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree.pickle"))
        resolver.write(os.path.join(cwd, "../testdata/tree.json"), "json")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree.json"))

    def test_resolver_load_pickle(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        nodes = findall(resolver.tree)
        assert len(nodes) == 12086
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 8100

    def test_resolver_load_json(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.json"), "json")
        nodes = findall(resolver.tree)
        assert len(nodes) == 12086
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 8100

    def test_resolver_write_and_load(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        resolver.write(os.path.join(cwd, "../testdata/tree.json"), "json")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree.json"))

        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.json"), "json")
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

    def test_resolver_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        resolver.filter(os.path.join(cwd, "../testdata/taxids_filter.txt"))
        nodes = findall(resolver.tree)
        assert len(nodes) == 1001
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 593
        nodes = [node.name for node in PreOrderIter(resolver.tree)]
        assert len(nodes) == 1001
        nodes = [node.name for node in LevelOrderIter(resolver.tree)]
        assert len(nodes) == 1001
        human = find_by_attr(resolver.tree, "9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_filter_and_write(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        resolver.filter(os.path.join(cwd, "../testdata/taxids_filter.txt"))
        resolver.write(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_filtered.pickle"))
        resolver.write(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_filtered.json"))

    def test_resolver_filter_load(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        nodes = findall(resolver.tree)
        assert len(nodes) == 1001
        nodes = findall(resolver.tree, filter_=lambda n: n.rank == "species")
        assert len(nodes) == 593
        nodes = [node.name for node in PreOrderIter(resolver.tree)]
        assert len(nodes) == 1001
        nodes = [node.name for node in LevelOrderIter(resolver.tree)]
        assert len(nodes) == 1001
        human = find_by_attr(resolver.tree, "9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_resolver_search(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        tax_ids = resolver.search(os.path.join(cwd, "../testdata/taxids_search.txt"),
                                  os.path.join(cwd, "../testdata/taxids_filter.txt"))
        assert len(tax_ids) == 302

    def test_resolver_validate(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        assert resolver.validate(os.path.join(cwd, "../testdata/taxids_validate.txt"),
                                 os.path.join(cwd, "../testdata/taxids_filter.txt"))

    def test_resolver_validate_alt(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        assert not resolver.validate(os.path.join(cwd, "../testdata/taxids_validate_alt.txt"),
                                     os.path.join(cwd, "../testdata/taxids_filter.txt"))

    def test_search_by_taxid(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        human = resolver.find_by_taxid("9606")
        assert human.rank == "species"
        assert human.parent.rank == "genus"
        assert human.parent.taxonName == "Homo"
        assert human.parent.parent.rank == "subfamily"
        assert human.parent.parent.taxonName == "Homininae"

    def test_validate_by_taxid(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        assert resolver.validate_by_taxid("9606")
        with pytest.raises(AssertionError):
            assert resolver.validate_by_taxid("000")

    def test_search_by_taxid(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_filtered.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        taxids = resolver.search(["9606"])
        assert len(taxids) == 3
