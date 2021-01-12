#################
Taxonomy Resolver
#################

Taxonomy Resolver builds NCBI Taxonomy Trees and lists of Taxonomy Identifiers (TaxIDs)
based on the `NCBI Taxonomy`_ Database.

Main features of Taxonomy Resolver are:

1. Downloading taxonomy dump files from the `NCBI ftp server`_
2. Building NCBI Taxonomy Trees (with `anytree`_)
3. Writing out the Tree in ``json`` or ``pickle`` formats
4. Filtering the Tree based on a list of TaxIDs
5. Quick lookup to see if a TaxID exists in the Tree
6. Generate lists of all children TaxIDs that compose a particular Node


------------

.. contents:: **Table of Contents**
   :depth: 3


Dependencies and Installation
=============================

Installation requires `Python`_ 3.7+ (recommended version 3.8). Additional requirements, which will be
downloaded and installed automatically. See full list of dependencies in `requirements.txt`_

Python Environment
------------------

Dependencies for the Python tools developed here, are the typical Python stack (3.6+ and pip).
A good approach is to set a virtual environment:

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

  python setup.py

``Taxonomy Resolver`` module will be available within your environment.

(TODO - Add the module to pypi!) Alternatively ``Taxonomy Resolver`` can be installed with pip:

.. code-block:: bash

  pip install taxonresolver


Getting Started
===============

Taxonomy Resolver can be used as Python module or via the CLI provided.

Module
------

Example of typical usage of the Taxonomy Resolver module is provided below:

.. code-block:: python

  from taxonresolver import TaxonResolver

  resolver = TaxonResolver()

  # Download the NCBI Taxonomy Data Dump
  dumpfile = "taxdump.zip"
  resolver.download(dumpfile, "zip")

  # Building the NCBI Taxonomy Tree (can take several minutes to build)
  resolver.build(dumpfile)
  # the resolver.tree can be saved to file at this stage with `resolver.write()`

  # Filtering the Tree based on a set of local TaxIDs (species-level)
  # A minimal Tree is constructed that covers (hierarchically) all TaxIDs provided
  filterfile = "taxids_filter.txt"
  resolver.filter(filterfile)

  # Saving the filtered Tree as JSON format
  treefile = "tree_filtered.json"
  resolver.write(treefile, "json")

  # Get a list of TaxIDs (species-level) that compose a set of TaxIDs
  searchfile = "taxids_search.txt"
  tax_ids = resolver.search(searchfile, filterfile) # the filterfile is optional
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

  # Filtering the Tree based on a set of local TaxIDs (species-level)
  filterfile = "taxids_filter.txt"
  resolver.filter(filterfile)

  # Validate a set of TaxIDs against the Tree and against a list of TaxIDs (species-level)
  validatefile = "taxids_validate.txt"
  valid = resolver.validate(validatefile, filterfile) # the filterfile is optional
  if valid:
    print(f"TaxIDs in {validatefile} are valid!")


Because each node in Taxonomy Resolver is an `anytree`_ node, all anytree features are available,
including Tree ``Rendering``, ``Iteration``, ``Searching``, etc. See `anytree's documentation`_ for more information on what is possible.

.. code-block:: python

  from taxonresolver import TaxonResolver
  from anytree.search import find_by_attr, findall_by_attr

  resolver = TaxonResolver()

  # Loading the NCBI Taxonomy Tree
  treefile = "tree.pickle"
  resolver.load(treefile, "pickle")

  # Tree is a dictionary of anytree Nodes
  tree = resolver.tree

  # Display the path of particular node
  # ( "9606" is the TaxID of species 'homo sapiens')
  find_by_attr(tree, "9606")
  # Node('/1/131567/(...)/9606', parentTaxId='9605', rank='species', taxonName='Homo sapiens')
  # Display the parent node
  find_by_attr(tree, "9606").parent
  # Node('/1/131567/(...)/9605', parentTaxId='207598', rank='genus', taxonName='Homo')
  # ( "40674" is the TaxID of class 'Mammalia')
  find_by_attr(tree, "40674")
  # Node('/1/131567/.../40674', parentTaxId='32524', rank='class', taxonName='Mammalia')

  # Iterate over all Nodes that compose a particular TaxID
  from anytree.iterators import LevelOrderIter
  # ( "9443" is the TaxID of order 'Primates')
  [node.name for node in LevelOrderIter(findall_by_attr(tree, "9443")) if node.rank == "species"]
  # [..., ..., ...]

CLI
---

Explore the CLI and each command by running
``python taxonomy_resolver.py (COMMAND) --help``. If Taxonomy Resolver was installed with
``python setup.py install``, then simply run ``taxonomy_resolver --help``:

.. code-block:: bash

  Usage: taxonomy_resolver [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                              [ARGS]...]...

    Taxonomy Resolver: Build NCBI Taxonomy Trees and lists of TaxIDs.

  Options:
    --version   Show the version and exit.
    -h, --help  Show this message and exit.

  Commands:
    build     Build NCBI Taxonomy Tree in JSON or Pickle.
    download  Download the NCBI Taxonomy dump file.
    search    Searches a NCBI Taxonomy Tree and writes a list of TaxIDs.
    validate  Validates a list of TaxIDs against a NCBI Taxonomy Tree.



Getting the NCBI Taxonomy Data from the `NCBI ftp server`_:

.. code-block:: bash

  python taxonomy-resolver.py download -out taxdump.zip


Building a Tree structure from the ``taxdump.zip`` file and saving it in JSON (or alternatively in ``pickle`` format):

.. code-block:: bash

  python taxonomy-resolver.py build -in taxdump.zip -out tree.json -outf json


Loading a built Tree structure in JSON and saving it in ``pickle`` format:

.. code-block:: bash

  python taxonomy-resolver.py build -in tree.json -inf json -out tree.pickle -outf pickle


Filtering an existing Tree structure in ``pickle`` format by passing a file containing a list of TaxIDs, and saving it in ``pickle`` format:

.. code-block:: bash

  python taxonomy-resolver.py build -in tree.pickle -inf pickle -out tree_filtered.pickle -outf pickle -taxidf taxids_filter.txt


Generating a list of TaxIDs that compose the hierarchy based on list of TaxIDs passed to search
a filtered Tree in ``pickle`` format:

.. code-block:: bash

  python taxonomy-resolver.py search -in tree_filtered.pickle -inf pickle -taxids taxids_search.txt -taxidf taxids_filter.txt -out taxids_list.txt


Validating a list of TaxIDs against a full (or filtered) Tree in ``pickle`` format:

.. code-block:: bash

  python taxonomy-resolver.py validate -in tree.pickle -inf pickle -taxids taxids_search.txt


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
.. _anytree: https://github.com/c0fec0de/anytree
.. _anytree's documentation: https://anytree.readthedocs.io/
.. _CHANGELOG.rst: CHANGELOG.rst
