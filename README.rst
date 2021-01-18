#################
Taxonomy Resolver
#################

Taxonomy Resolver builds an NCBI Taxonomy Tree structure based on the `NCBI Taxonomy`_ Database classification. Taxonomy Resolver can be used to validate Taxonomy Identifiers (TaxIDs) against the Tree or to generate lists of TaxIDs, based on some TaxID of interest (e.g. higher-level rank (node) in the tree).

The main features of Taxonomy Resolver are:

1. Downloading taxonomy dump files from the `NCBI ftp server`_
2. Building an NCBI Taxonomy Tree data structure based on the NCBI Taxonomy classification
3. Writing and loading the Tree structure in ``pickle`` format
4. Quick lookup to see if a TaxID exists in the Tree (i.e. is valid)
5. Generate lists of all children TaxIDs that compose a particular Node
6. Generate lists of children TaxIDs based on a list of included and excluded TaxIDs
7. Filtering the resulting list of children TaxIDs, for example to cleanup TaxIDs that are not observed in a dataset of interest

------------

.. contents:: **Table of Contents**
   :depth: 3


Dependencies and Installation
=============================

Installation requires `Python`_ 3.7+ (recommended version 3.9). Additional requirements, which will be downloaded and installed automatically. See full list of dependencies in `requirements.txt`_

Python Environment
------------------

Dependencies for the Python tools developed here, are the typical Python stack (3.7+ and pip). A good approach is to set a virtual environment:

.. code-block:: bash

  virtualenv -p `which python` env
  source ./env/bin/activate
  pip install --upgrade -r requirements.txt
  pip freeze > requirements_from_freeze.txt
  deactivate

Installing
----------

Download the source code or clone the repository, then simply run:

.. code-block:: bash

  python setup.py install

``Taxonomy Resolver`` module will be available within your environment.

(TODO - Add the module to pypi!) Alternatively ``Taxonomy Resolver`` can be installed with pip:

.. code-block:: bash

  pip install taxonresolver


Getting Started
===============

Taxonomy Resolver can be used as a Python module or via the CLI provided.

Module
------

Example of typical usage of the Taxonomy Resolver module is provided below:

.. code-block:: python

  from taxonresolver import TaxonResolver

  resolver = TaxonResolver()

  # Download the NCBI Taxonomy Data Dump
  dumpfile = "taxdmp.zip"
  resolver.download(dumpfile, "zip")

  # Building the NCBI Taxonomy Tree data structure
  resolver.build(dumpfile)

  # Saving the Tree data structure as Pickle format
  treefile = "tree.pickle"
  resolver.write(treefile, "pickle")

  # Get a list of children TaxIDs that compose a set of TaxIDs
  searchfile = "taxids_search.txt"
  tax_ids = resolver.search(searchfile)
  # Write the TaxIDs to a file
  taxidsfile = "taxids_list.txt"
  with open(outfile, "w") as outfile:
      outfile.write("\n".join(tax_ids))


When a Taxonomy Tree is already available one can simply load it with ``resolver.load()``:

.. code-block:: python

  from taxonresolver import TaxonResolver

  resolver = TaxonResolver()

  # Loading the NCBI Taxonomy Tree
  treefile = "tree.pickle"
  resolver.load(treefile, "pickle")

  # Validate a set of TaxIDs against the Tree data structure
  validatefile = "taxids_validate.txt"
  valid = resolver.validate(validatefile)
  if valid:
    print(f"TaxIDs in {validatefile} are valid!")

CLI
---

Explore the CLI and each command by running
``python taxonomy_resolver.py (COMMAND) --help``. If Taxonomy Resolver was installed with
``python setup.py install``, then simply run ``taxonomy_resolver --help``:

.. code-block:: bash

  Usage: taxonomy_resolver [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                              [ARGS]...]...

    Taxonomy Resolver: Build a NCBI Taxonomy Tree, validate and search TaxIDs.

  Options:
    --version   Show the version and exit.
    -h, --help  Show this message and exit.

  Commands:
    build     Build a NCBI Taxonomy Tree data structure.
    download  Download the NCBI Taxonomy dump file ('taxdmp.zip').
    search    Searches a Tree data structure and writes a list of TaxIDs.
    validate  Validates a list of TaxIDs against a Tree data structure.


Getting the NCBI Taxonomy Data from the `NCBI ftp server`_:

.. code-block:: bash

  python taxonomy-resolver.py download -out taxdmp.zip


Building a Tree structure from the ``taxdmp.zip`` file and saving it in JSON (or alternatively in ``pickle`` format):

.. code-block:: bash

  python taxonomy-resolver.py build -in taxdmp.zip -out tree.pickle


Load a previously built Tree data structure in ``pickle`` format and generating a list of TaxIDs that compose the hierarchy based on list of TaxIDs:

.. code-block:: bash

  python taxonomy-resolver.py search -in tree.pickle -taxids testdata/taxids_search.txt

Load a previously built Tree data structure in ``pickle`` format and generating a list of TaxIDs (included TaxIDs), exclude TaxIDs from the search (excluded TaxIDs), and filter the final result to only those TaxIDs that are available in the list of filter TaxIDs (filtered TaxIDs):

.. code-block:: bash

  python taxonomy-resolver.py search -in tree.pickle -taxids testdata/taxids_search.txt -taxidse testdata/taxids_exclude.txt -taxidsf testdata/taxids_filter.txt -out taxids_list.txt


Validating a list of TaxIDs against a Tree data structure in ``pickle`` format:

.. code-block:: bash

  python taxonomy-resolver.py validate -in tree.pickle -taxids testdata/taxids_validate.txt


Bug Tracking
============

If you find any bugs or issues please log them in the `issue tracker`_.

Changelog
=========

See release notes on `CHANGELOG.rst`_

Credits
=======

* Fábio Madeira <fmadeira@ebi.ac.uk>
* Adrian Tivey <ativey@ebi.ac.uk>

Licensing
=========

Apache License 2.0. See `license`_ for details.

.. links
.. _license: LICENSE
.. _issue tracker: ../../issues
.. _requirements.txt: requirements.txt
.. _Python: https://www.python.org/
.. _NCBI Taxonomy: https://www.ncbi.nlm.nih.gov/taxonomy
.. _NCBI ftp server: https://ftp.ncbi.nih.gov/pub/taxonomy/
.. _CHANGELOG.rst: CHANGELOG.rst
