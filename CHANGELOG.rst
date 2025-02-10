**1.1.1**

- Minor improvements and fixes for the JOSS paper
- Adds documentation about ``newick`` to `README.rst`_

**1.1.0**

- Adds ``newick`` output format, available on the build and search CLI commands
- Adds progress reporting powered by `tqdm`_ for taxonomy download, reading, building and searching
- Adds CLI tests, improves tree tests and increases test coverage overall
- Some other improvements and updates to `README.rst`_

**1.0.0**

- First major release 🎉
- Updates to `README.rst`_
- Added `CONTRIBUTING.rst`_
- Renamed module to ``taxonomyresolver``

**0.3.2**

- Updates README

**0.3.1**

- Fixed the 'publishing to PyPI' action

**0.3.0**

- Moved to use pyproject.toml and `Poetry`_ for packaging
- Improved type hint annotations 

**0.2.1**

- Re-added the "filter" option to the `TaxonResolver` class and CLI
- Several improvements in usability and consistency

**0.2.0**

- Improved performance with Nested Sets
- Added new `pandas` dependency
- Tree "schema" stored as a pandas ``DataFrame``
- Modified Preorder Tree Traversal markup is used for quick tree search
- Improved search times by reducing the number of subtrees searched
- Additional optimisations by using Python ``sets``
- Updated description in the ``README.rst``

**0.1.0**

- Removed the "Any Python Tree" `anytree` dependency
- Large refactoring and rewrite of the `TaxonResolver` class
- Removed `TaxonResolverFast` and `fast` mode
- New test cases based on a mock tree `testdata/nodes_mock.dmp`
- Simplified usage of the class and CLI
- Only currently working with `pickle` format for writing and loading
- Searching takes included, excluded and filter lists of TaxIDs
- Validation only takes included TaxIDs
- CLI `search` and `validate` can take multiple TaxIDs at once

**0.0.6**

- Additional fixes and improvements for missing and invalid TaxIDs

**0.0.5**

- Brought TaxonResolverFast in line with the functionality of TaxonResolver
- Searching and validation based on lists of TaxIDs (instead of relying only on files)
- Updated CLI to take multiple filter files
- Updated CLI to take comma-separated values for search and validation
- CLI writes to STDOUT by default for search and validation

- Capturing a list TaxIDs used for `filter`, which allows searching and validation without having to provide them again

**0.0.4**

- Fixed the logic under validation and searching
- Added `TaxonResolverFast` class for faster searching and validation (but it requires a built Tree)
- Added `--mode 'fast'` mode to the CLI

**0.0.3**

- Improved filtering and searching functions
- Searching performs validation to prevent searching exceptions/errors
- Added search/validate 'by taxid' methods
- Added cached search as an option

**0.0.2**

- Added wrapper class and methods to work with the Taxonomy Resolver
- Added functions to build a Tree and converting it to `anytree` Tree (with re-parenting)
- Added command-line interface (CLI) with sub-commands for common functions

**0.0.1**

- Started development

.. links
.. _Poetry: https://python-poetry.org/
.. _CONTRIBUTING.rst: CONTRIBUTING.rst
.. _README.rst: README.rst
.. _tqdm: https://github.com/tqdm/tqdm