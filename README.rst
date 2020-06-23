#################
Taxonomy Resolver
#################

Taxonomy Resolver builds lists of taxonomy Identifiers based on the `NCBI Taxonomy`_ Database.


.. contents:: **Table of Contents**
   :depth: 3


Dependencies and Installation
=============================

Installation requires `Python`_ 3.6+ (recommended version 3.8). Additional requirements, which will be
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


Getting Started
===============

Taxonomy Resolver can be used as Python module or via the CLI provided. Examples below are
provided running the CLI, but looking over the CLI source code illustrates most of the
functionality and how Taxonomy Resolver can be used as a module.


Getting the NCBI Taxonomy Data from the `NCBI ftp server`_:

.. code-block:: bash

  python taxonomy_resolver_cli.py download -out ./ncbi-taxonomy/taxdump.zip


Building a Tree structure from the `taxdump.zip` file and saving it in JSON (or alternatively in `pickle` format):

.. code-block:: bash

  python taxonomy_resolver_cli.py build -in ./ncbi-taxonomy/taxdump.zip -out ./ncbi-taxonomy/tree.json -outf json


Loading a built Tree structure in JSON and saving it in `pickle` format:

.. code-block:: bash

  python taxonomy_resolver_cli.py build -in ./ncbi-taxonomy/tree.json -inf json -out ./ncbi-taxonomy/tree.pickle -outf pickle


Filtering an existing Tree structure in `pickle` format by passing a file containing a list of TaxIDs, and saving it in `pickle` format:

.. code-block:: bash

  python taxonomy_resolver_cli.py build -in ./ncbi-taxonomy/tree.pickle -inf pickle -out ./ncbi-taxonomy/tree_filtered.pickle -outf pickle -taxidf ./ncbi-taxonomy/taxids_filter.txt


Generating a list of TaxIDs that compose the hierachy based on list of TaxIDs passed to search
a filtered Tree in `pickle` format:

.. code-block:: bash

  python taxonomy_resolver_cli.py search -in ./ncbi-taxonomy/tree_filtered.pickle -inf pickle -taxids ./ncbi-taxonomy/taxids_search.txt -taxidf ./ncbi-taxonomy/taxids_filter.txt -out ./ncbi-taxonomy/taxids_list.txt


Bug Tracking
============

If you find any bugs or issues please log them in the `issue tracker`_.

Changelog
=========

**0.0.1**

- Started development

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