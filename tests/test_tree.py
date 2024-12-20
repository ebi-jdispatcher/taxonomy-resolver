#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2024.
:license: Apache 2.0, see LICENSE for more details.
"""

import os

import pytest

from taxonomyresolver import TaxonResolver
from taxonomyresolver.utils import load_logging


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
    def test_download_taxdmp(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.download(os.path.join(cwd, f"../testdata/taxdmp.zip"), "zip")
        assert os.path.isfile(os.path.join(cwd, "../testdata/taxdmp.zip"))

    @pytest.mark.skip(reason="Skip test by default!")
    def test_resolver_build(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdmp.zip"))
        if resolver.tree is not None:
            assert len(resolver.tree) == 2631861

    def test_resolver_build_and_write(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdmp.zip"))
        if resolver.tree is not None:
            assert len(resolver.tree) == 2631861
        resolver.write(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree.pickle"))

    def test_resolver_load_pickle(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        if resolver.tree is not None:
            assert len(resolver.tree) == 2631861

    def test_resolver_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        resolver.filter(os.path.join(cwd, "../testdata/taxids_filter.txt"))
        if resolver.tree is not None:
            assert len(resolver.tree) == 1003

    def test_resolver_filter_and_write(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        resolver.filter(os.path.join(cwd, "../testdata/taxids_filter.txt"))
        if resolver.tree is not None:
            assert len(resolver.tree) == 1003
        resolver.write(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_filtered.pickle"))

    def test_resolver_filter_load(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_filtered.pickle"), "pickle")
        if resolver.tree is not None:
            assert len(resolver.tree) == 1003

    def test_resolver_search_by_taxid_human(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["9606"])
        if taxids:
            assert len(taxids) == 3

    def test_resolver_search_by_taxid_bacteria(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["2"])
        if taxids:
            assert len(taxids) == 577322

    def test_resolver_search_by_taxid_archaea(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["2157"])
        if taxids:
            assert len(taxids) == 14866

    def test_resolver_search_by_taxid_eukaryota(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["2759"])
        if taxids:
            assert len(taxids) == 1760410

    def test_resolver_search_by_taxid_viruses(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["10239"])
        if taxids:
            assert len(taxids) == 258680

    def test_resolver_search_by_taxid_other(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["28384"])
        if taxids:
            assert len(taxids) == 19466

    def test_resolver_search_by_taxid_unclassified(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["12908"])
        if taxids:
            assert len(taxids) == 1113

    def test_resolver_search_by_taxid_mammalia(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["40674"])
        if taxids:
            assert len(taxids) == 14213

    def test_resolver_search_by_taxid_primates(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["9443"])
        if taxids:
            assert len(taxids) == 1132

    def test_resolver_search_by_taxid_plants(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["3193"])
        if taxids:
            assert len(taxids) == 255378

    def test_resolver_search(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(
            taxidinclude=os.path.join(cwd, "../testdata/taxids_search.txt")
        )
        if taxids:
            assert len(taxids) == 593

    def test_resolver_search_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(
            taxidinclude=os.path.join(cwd, "../testdata/taxids_search.txt"),
            taxidfilter=os.path.join(cwd, "../testdata/taxids_filter.txt"),
        )
        if taxids:
            assert len(taxids) == 300

    def test_resolver_search_exclude_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(
            taxidinclude=os.path.join(cwd, "../testdata/taxids_search.txt"),
            taxidexclude=os.path.join(cwd, "../testdata/taxids_exclude.txt"),
            taxidfilter=os.path.join(cwd, "../testdata/taxids_filter.txt"),
        )
        if taxids:
            assert len(taxids) == 294

    def test_resolver_validate(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert resolver.validate(os.path.join(cwd, "../testdata/taxids_validate.txt"))

    def test_resolver_validate_alt(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert not resolver.validate(
            os.path.join(cwd, "../testdata/taxids_validate_alt.txt")
        )

    def test_resolver_build_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/nodes_mock.dmp"))
        if resolver.tree is not None:
            assert len(resolver.tree) == 29

    def test_resolver_build_and_write_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/nodes_mock.dmp"))
        resolver.write(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_mock.pickle"))

    def test_resolver_load_pickle_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        if resolver.tree is not None:
            assert len(resolver.tree) == 29

    def test_resolver_filter_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        resolver.filter(taxidfilter=["12", "21"])
        if resolver.tree is not None:
            assert len(resolver.tree) == 9
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        resolver.filter(taxidfilter=["10", "21", "24"])
        if resolver.tree is not None:
            assert len(resolver.tree) == 17
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        resolver.filter(taxidfilter=["10", "21", "9", "27"])
        if resolver.tree is not None:
            assert len(resolver.tree) == 19
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        resolver.filter(taxidfilter=["19", "25", "22", "29"])
        if resolver.tree is not None:
            assert len(resolver.tree) == 18

    def test_resolver_filter_and_write_mock(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        resolver.filter(taxidfilter=["12", "21"])
        if resolver.tree is not None:
            assert len(resolver.tree) == 9
        resolver.write(
            os.path.join(cwd, "../testdata/tree_mock_filtered.pickle"), "pickle"
        )
        assert os.path.isfile(
            os.path.join(cwd, "../testdata/tree_mock_filtered.pickle")
        )

    def test_resolver_filter_load_mock(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(
            os.path.join(cwd, "../testdata/tree_mock_filtered.pickle"), "pickle"
        )
        if resolver.tree is not None:
            assert len(resolver.tree) == 9

    def test_resolver_search_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxids = resolver.search(taxidinclude=["4"])
        if taxids:
            assert len(taxids) == 14
        taxids = resolver.search(taxidinclude=["5"])
        if taxids:
            assert len(taxids) == 9
        taxids = resolver.search(taxidinclude=["29"])
        if taxids:
            assert len(taxids) == 1
        taxids = resolver.search(taxidinclude=["4", "10", "12", "14"])
        if taxids:
            assert len(taxids) == 21
        taxids = resolver.search(taxidinclude=["7", "11", "21", "27", "29"])
        if taxids:
            assert len(taxids) == 9
        taxids = resolver.search(taxidinclude=["7", "11", "5", "21", "27", "29"])
        if taxids:
            assert len(taxids) == 14

    def test_resolver_search_exclude_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxids = resolver.search(taxidinclude=["4"], taxidexclude=["24"])
        if taxids:
            assert len(taxids) == 10
        taxids = resolver.search(taxidinclude=["5"], taxidexclude=["12"])
        if taxids:
            assert len(taxids) == 4
        taxids = resolver.search(taxidinclude=["29"], taxidexclude=["3"])
        if taxids:
            assert len(taxids) == 1

    def test_resolver_search_filter_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxidfilter = ["19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29"]
        taxids = resolver.search(taxidinclude=["4"], taxidfilter=taxidfilter)
        if taxids:
            assert len(taxids) == 6
        taxids = resolver.search(taxidinclude=["5"], taxidfilter=taxidfilter)
        if taxids:
            assert len(taxids) == 5

    def test_resolver_search_exclude_filter_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxidfilter = ["19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29"]
        taxids = resolver.search(
            taxidinclude=["4"], taxidexclude=["24"], taxidfilter=taxidfilter
        )
        if taxids:
            assert len(taxids) == 2
        taxids = resolver.search(
            taxidinclude=["5"], taxidexclude=["12"], taxidfilter=taxidfilter
        )
        if taxids:
            assert len(taxids) == 1

    def test_resolver_validate_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        assert resolver.validate(taxidinclude=["8"])
        assert resolver.validate(taxidinclude=["9"])
        assert resolver.validate(taxidinclude=["10"])
        assert not resolver.validate(taxidinclude=["9606"])
