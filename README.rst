#################
Taxonomy Resolver
#################

Taxonomy Resolver builds lists of taxonomy Identifiers based on the `NCBI Taxonomy`_ Database.


.. contents:: **Table of Contents**
   :depth: 3


Dependencies and Installation
=============================

Installation requires `Python`_ 3.6+ (recommended version 3.7). Additional requirements, which will be
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

Getting the NCBI Taxonomy Data from the `NCBI ftp server`_ and preparing the data:

code-block:: bash

  cd ncbi-taxonomy
  # download the dump from the ftp
  wget https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
  # then
  gunzip -c taxdump.tar.gz | tar xf -


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

Licensing
=========

Apache License 2.0. See `license`_ for details.

.. links
.. _license: LICENSE
.. _issue tracker: ../../issues
.. _Python: https://www.python.org/
.. _NCBI Taxonomy: https://www.ncbi.nlm.nih.gov/taxonomy
.. _NCBI ftp server: https://ftp.ncbi.nih.gov/pub/taxonomy/