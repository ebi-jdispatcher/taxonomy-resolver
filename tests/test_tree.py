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
    def test_download_taxdump(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.download(os.path.join(cwd, f"../testdata/taxdump.zip"), "zip")
        assert os.path.isfile(os.path.join(cwd, "../testdata/taxdump.zip"))

    def test_resolver_build(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdump.zip"))
        assert len(resolver.tree) == 2302938

    def test_resolver_build_and_write(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.build(os.path.join(cwd, "../testdata/taxdump.zip"))
        resolver.write(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert os.path.isfile(os.path.join(cwd, "../testdata/tree.pickle"))

    def test_resolver_load_pickle(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert len(resolver.tree) == 2302938

    def test_search_by_taxid_human(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        taxids = resolver.search(["9606"])
        assert len(taxids) == 3

    def test_resolver_search(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        tax_ids = resolver.search(os.path.join(cwd, "../testdata/taxids_search.txt"))
        assert len(tax_ids) == 533

    def test_resolver_search_filter(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        tax_ids = resolver.search(os.path.join(cwd, "../testdata/taxids_search.txt"),
                                  os.path.join(cwd, "../testdata/taxids_filter.txt"))
        assert len(tax_ids) == 302

    def test_resolver_validate(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert resolver.validate(os.path.join(cwd, "../testdata/taxids_validate.txt"))

    def test_resolver_validate_alt(self, context, cwd):
        resolver = TaxonResolver(logging=context)
        resolver.load(os.path.join(cwd, "../testdata/tree.pickle"), "pickle")
        assert not resolver.validate(os.path.join(cwd, "../testdata/taxids_validate_alt.txt"))
