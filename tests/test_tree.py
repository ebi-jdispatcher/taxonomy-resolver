#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2021.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
import pytest

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
    def test_download_taxdmp(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.download(os.path.join(cwd, f"../testdata/taxdmp.zip"), "zip")
        assert os.path.isfile(os.path.join(cwd, "../testdata/taxdmp.zip"))

    def test_resolver_build(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdmp.zip"))
        assert len(resolver.tree) == 2302938

    def test_resolver_build_and_write(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdmp.zip"))
        resolver.write(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree.pickle"))

    def test_resolver_load_pickle(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert len(resolver.tree) == 2302938

    def test_resolver_search_by_taxid_human(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["9606"])
        assert len(taxids) == 3

    def test_resolver_search(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        tax_ids = resolver.search(taxidinclude=os.path.join(cwd, "../testdata/taxids_search.txt"))
        assert len(tax_ids) == 533

    def test_resolver_search_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        tax_ids = resolver.search(taxidinclude=os.path.join(cwd, "../testdata/taxids_search.txt"),
                                  taxidfilter=os.path.join(cwd, "../testdata/taxids_filter.txt"))
        assert len(tax_ids) == 302

    def test_resolver_search_exclude_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        tax_ids = resolver.search(taxidinclude=os.path.join(cwd, "../testdata/taxids_search.txt"),
                                  taxidexclude=os.path.join(cwd, "../testdata/taxids_exclude.txt"),
                                  taxidfilter=os.path.join(cwd, "../testdata/taxids_filter.txt"))
        assert len(tax_ids) == 296

    def test_resolver_validate(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert resolver.validate(os.path.join(cwd, "../testdata/taxids_validate.txt"))

    def test_resolver_validate_alt(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert not resolver.validate(os.path.join(cwd, "../testdata/taxids_validate_alt.txt"))

    def test_resolver_build_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/nodes_mock.dmp"))
        assert len(resolver.tree) == 29

    def test_resolver_build_and_write_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/nodes_mock.dmp"))
        resolver.write(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_mock.pickle"))

    def test_resolver_load_pickle_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        assert len(resolver.tree) == 29

    def test_resolver_search_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxids = resolver.search(taxidinclude=["4"])
        assert len(taxids) == 14
        taxids = resolver.search(taxidinclude=["5"])
        assert len(taxids) == 9
        taxids = resolver.search(taxidinclude=["29"])
        assert len(taxids) == 1

    def test_resolver_search_exclude_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxids = resolver.search(taxidinclude=["4"], taxidexclude=["24"])
        assert len(taxids) == 10
        taxids = resolver.search(taxidinclude=["5"], taxidexclude=["12"])
        assert len(taxids) == 4
        taxids = resolver.search(taxidinclude=["29"], taxidexclude=["3"])
        assert len(taxids) == 1

    def test_resolver_search_filter_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxidfilter = ["19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29"]
        taxids = resolver.search(taxidinclude=["4"], taxidfilter=taxidfilter)
        assert len(taxids) == 6
        taxids = resolver.search(taxidinclude=["5"], taxidfilter=taxidfilter)
        assert len(taxids) == 5

    def test_resolver_search_exclude_filter_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        taxidfilter = ["19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29"]
        taxids = resolver.search(taxidinclude=["4"], taxidexclude=["24"],
                                 taxidfilter=taxidfilter)
        assert len(taxids) == 2
        taxids = resolver.search(taxidinclude=["5"], taxidexclude=["12"],
                                 taxidfilter=taxidfilter)
        assert len(taxids) == 1

    def test_resolver_validate_mock_tree(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_mock.pickle"), "pickle")
        assert resolver.validate(taxidinclude=["8"])
        assert resolver.validate(taxidinclude=["9"])
        assert resolver.validate(taxidinclude=["10"])
        assert not resolver.validate(taxidinclude=["9606"])