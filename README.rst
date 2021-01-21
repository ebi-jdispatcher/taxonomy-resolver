#################
Taxonomy Resolver
#################

Taxonomy Resolver builds an NCBI Taxonomy Tree structure based on the `NCBI Taxonomy`_ Database classification. Taxonomy Resolver can be used to validate Taxonomy Identifiers (TaxIDs) against the Tree or to generate lists of TaxIDs, based on some TaxID of interest (e.g. higher-level rank (node) in the tree).

The main features of Taxonomy Resolver are:

1. Downloading taxonomy dump files from the `NCBI ftp server`_
2. Building an NCBI Taxonomy Tree data structure based on the NCBI Taxonomy classification
3. Writing and loading the Tree structure in ``pickle`` format
4. Quick lookup to see if a TaxID exists in the Tree (i.e. is valid)
5. Generate lists of all children TaxIDs that compose a particular Node (sub-tree)
6. Generate lists of children TaxIDs based on a list of included and excluded TaxIDs (included and excluded sub-trees)
7. Filtering the resulting list of children TaxIDs, for example to cleanup TaxIDs that are not observed in a dataset of interest

Taxonomy Resolver initially builds a tree structure based on recursively assigning the children nodes of a particular node. To retrieve a full tree or sub-tree, a lot of iteration takes place, to follow the path from the node of interest down the hierarchy. This approach does not perform well, especially for large trees. Thus, in Taxonomy Resolver, the tree is then represented following a different approach, commonly referred to as the Nested Set Model. In the Nested Set Model, we can look at a tree hierarchy differently, not as connected nodes, but as nested containers. The nested set model is a particular technique for representing nested sets in relational databases, i.e. which we implement here in a pandas ``DataFrame``. For that, the full tree is traversed with Modified Preorder Tree Traversal strategy. In a preorder traversal, the root node is visited first, then recursively do a preorder traversal of the left sub-tree, followed by a recursive preorder traversal of the right subtree, in order until every node has been visited. The modified strategy allows us to capture the 'left' and 'right' (``lft`` and ``rgt``, respectively) boundaries of each nested container
Querying and searching is much faster with this approach because finding a subtree is as simple as filtering/searching for the nodes where ``lft > Node's lft`` and ``rgt < Node's rgt``.

Both traversal markup (left and right), depth and node indexes are captured for each node in the tree. The following Taxonomy Tree is used as a mock test case - see `nodes_mock.dmp`_:

.. image:: testdata/mock_tree_diagram.png
  :width: 700px

The resulting tree can be represented in tabular form:

+-------+--------+-----------+--------+-------+-----+-----+
| index | tax_id | parent_id | rank   | depth | lft | rgt |
+=======+========+===========+========+=======+=====+=====+
| 1     | 1      | 1         | root   | 1     | 1   | 58  |
+-------+--------+-----------+--------+-------+-----+-----+
| 2     | 2      | 1         | rank 2 | 2     | 2   | 57  |
+-------+--------+-----------+--------+-------+-----+-----+
| 3     | 3      | 2         | rank 3 | 3     | 3   | 28  |
+-------+--------+-----------+--------+-------+-----+-----+
| 4     | 5      | 3         | rank 4 | 4     | 4   | 21  |
+-------+--------+-----------+--------+-------+-----+-----+
| 5     | 10     | 5         | rank 5 | 5     | 5   | 8   |
+-------+--------+-----------+--------+-------+-----+-----+
| 6     | 19     | 10        | rank 6 | 6     | 6   | 7   |
+-------+--------+-----------+--------+-------+-----+-----+
| 7     | 11     | 5         | rank 5 | 5     | 9   | 10  |
+-------+--------+-----------+--------+-------+-----+-----+
| 8     | 12     | 5         | rank 5 | 5     | 11  | 20  |
+-------+--------+-----------+--------+-------+-----+-----+
| 9     | 20     | 12        | rank 6 | 6     | 12  | 13  |
+-------+--------+-----------+--------+-------+-----+-----+
| 10    | 21     | 12        | rank 6 | 6     | 14  | 19  |
+-------+--------+-----------+--------+-------+-----+-----+
| 11    | 25     | 21        | rank 7 | 7     | 15  | 16  |
+-------+--------+-----------+--------+-------+-----+-----+
| 12    | 26     | 21        | rank 7 | 7     | 17  | 18  |
+-------+--------+-----------+--------+-------+-----+-----+
| 13    | 6      | 3         | rank 4 | 4     | 22  | 23  |
+-------+--------+-----------+--------+-------+-----+-----+
| 14    | 7      | 3         | rank 4 | 4     | 24  | 27  |
+-------+--------+-----------+--------+-------+-----+-----+
| 15    | 13     | 7         | rank 5 | 5     | 25  | 26  |
+-------+--------+-----------+--------+-------+-----+-----+
| 16    | 4      | 2         | rank 3 | 3     | 29  | 56  |
+-------+--------+-----------+--------+-------+-----+-----+
| 17    | 8      | 4         | rank 4 | 4     | 30  | 39  |
+-------+--------+-----------+--------+-------+-----+-----+
| 18    | 14     | 8         | rank 5 | 5     | 31  | 36  |
+-------+--------+-----------+--------+-------+-----+-----+
| 19    | 22     | 14        | rank 6 | 6     | 32  | 33  |
+-------+--------+-----------+--------+-------+-----+-----+
| 20    | 23     | 14        | rank 6 | 6     | 34  | 35  |
+-------+--------+-----------+--------+-------+-----+-----+
| 21    | 15     | 8         | rank 5 | 5     | 37  | 38  |
+-------+--------+-----------+--------+-------+-----+-----+
| 22    | 9      | 4         | rank 4 | 4     | 40  | 55  |
+-------+--------+-----------+--------+-------+-----+-----+
| 23    | 16     | 9         | rank 5 | 5     | 41  | 42  |
+-------+--------+-----------+--------+-------+-----+-----+
| 24    | 17     | 9         | rank 5 | 5     | 43  | 44  |
+-------+--------+-----------+--------+-------+-----+-----+
| 25    | 18     | 9         | rank 5 | 5     | 45  | 54  |
+-------+--------+-----------+--------+-------+-----+-----+
| 26    | 24     | 18        | rank 6 | 6     | 46  | 53  |
+-------+--------+-----------+--------+-------+-----+-----+
| 27    | 27     | 24        | rank 7 | 7     | 47  | 52  |
+-------+--------+-----------+--------+-------+-----+-----+
| 28    | 28     | 27        | rank 8 | 8     | 48  | 49  |
+-------+--------+-----------+--------+-------+-----+-----+
| 29    | 29     | 27        | rank 8 | 8     | 50  | 51  |
+-------+--------+-----------+--------+-------+-----+-----+


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
.. _nodes_mock.dmp: testdata/nodes_mock.dmp
