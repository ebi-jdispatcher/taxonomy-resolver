#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
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
from taxonresolver import TaxonResolverFast
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
    def test_resolver_build(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdump.zip"))
        nodes = resolver.tree["nodes"]
        assert len(nodes) == 12099
        human = resolver.find_by_taxid("9606")
        assert human["parent_tax_id"] == "9605"
        assert human["rank"] == "species"

    def test_resolver_build_and_write(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdump.zip"))
        resolver.write(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_fast.pickle"))
        resolver.write(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_fast.json"))

    def test_resolver_load_pickle(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        nodes = resolver.tree["nodes"]
        assert len(nodes) == 12099

    def test_resolver_load_json(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        nodes = resolver.tree["nodes"]
        assert len(nodes) == 12099

    def test_resolver_write_and_load(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        resolver.write(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_fast.json"))

        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        nodes = resolver.tree["nodes"]
        assert len(nodes) == 12099
        human = resolver.find_by_taxid("9606")
        assert human["parent_tax_id"] == "9605"
        assert human["rank"] == "species"

    def test_resolver_filter(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        resolver.filter(os.path.join(cwd, "../testdata/taxids_filter.txt"))
        nodes = resolver.tree["nodes"]
        assert len(nodes) == 593

    def test_resolver_filter_and_write(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        resolver.filter(os.path.join(cwd, "../testdata/taxids_filter.txt"))
        resolver.write(os.path.join(cwd, "../testdata/tree_fast_filtered.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_fast_filtered.pickle"))
        resolver.write(os.path.join(cwd, "../testdata/tree_fast_filtered.json"), "json")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree_fast_filtered.json"))

    def test_resolver_filter_load(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree_fast_filtered.json"), "json")
        nodes = resolver.tree["nodes"]
        assert len(nodes) == 593

    def test_resolver_search(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        tax_ids = resolver.search(os.path.join(cwd, "../testdata/taxids_search.txt"),
                                  os.path.join(cwd, "../testdata/taxids_filter.txt"))
        assert len(tax_ids) == 302

    def test_resolver_validate(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        assert resolver.validate(os.path.join(cwd, "../testdata/taxids_validate.txt"),
                                 os.path.join(cwd, "../testdata/taxids_filter.txt"))

    def test_resolver_validate_alt(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        assert not resolver.validate(os.path.join(cwd, "../testdata/taxids_validate_alt.txt"),
                                     os.path.join(cwd, "../testdata/taxids_filter.txt"))

    def test_search_by_taxid(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        human = resolver.find_by_taxid("9606")
        assert human["parent_tax_id"] == "9605"
        assert human["rank"] == "species"

    def test_validate_by_taxid(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        assert resolver.validate_by_taxid("9606")
        with pytest.raises(AssertionError):
            assert resolver.validate_by_taxid("000")

    def test_search_by_taxid_human(self, context, cwd):
        resolver = TaxonResolverFast(logging=context)
        # resolver.load(os.path.join(cwd, "../testdata/tree_fast.json"), "json")
        resolver.load(os.path.join(cwd, "../testdata/tree_fast.pickle"), "pickle")
        taxids = resolver.search(["9606"])
        assert len(taxids) == 3
