Contributing to Taxonomy Resolver
=================================

Thank you for your interest in contributing to **Taxonomy Resolver**! We welcome all contributions to make this project better and more useful for the community. This document will guide you through the steps required to contribute to this project.

Table of Contents
-----------------

- `Getting Started <#getting-started>`_
- `How to Contribute <#how-to-contribute>`_
  - `Reporting Bugs <#reporting-bugs>`_
  - `Suggesting Features <#suggesting-features>`_
  - `Contributing Code <#contributing-code>`_
    - `Fork the Repository <#fork-the-repository>`_
    - `Create a Branch <#create-a-branch>`_
    - `Write Your Code <#write-your-code>`_
    - `Run Tests <#run-tests>`_
    - `Submit a Pull Request <#submit-a-pull-request>`_
- `Code Style <#code-style>`_
- `Testing <#testing>`_
- `Documentation <#documentation>`_
- `License <#license>`_

Getting Started
---------------

To start contributing:

1. Fork the repository from `taxonomy-resolver <https://github.com/ebi-jdispatcher/taxonomy-resolver>`_.
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/your-username/taxonomy-resolver.git

3. Install the necessary dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

4. Alternatively, use Poetry to install the necessary dependencies:

   .. code-block:: bash

      poetry install

Make sure to check the issues list before contributing. It helps to discuss your contribution idea beforehand, either by opening a new issue or commenting on an existing one.

How to Contribute
-----------------

Reporting Bugs
~~~~~~~~~~~~~~

If you encounter any bugs or unexpected behavior, feel free to open an issue on GitHub. When submitting an issue:

- Use a clear and descriptive title.
- Describe the steps to reproduce the problem.
- Mention the Python version and platform you're using.
- Include any relevant logs, screenshots, or error messages.

Suggesting Features
~~~~~~~~~~~~~~~~~~~

We welcome new feature suggestions! If you have an idea to improve **Taxonomy Resolver**, open an issue with:

- A detailed description of the feature.
- Potential use cases for the feature.
- Why the feature would be useful for the community.

Contributing Code
~~~~~~~~~~~~~~~~~

If you'd like to contribute code, follow these steps:

Fork the Repository
^^^^^^^^^^^^^^^^^^^

1. Fork the repository by clicking the "Fork" button on the top right of the repository page.
2. Clone the forked repository to your local machine:

   .. code-block:: bash

      git clone https://github.com/your-username/taxonomy-resolver.git

Create a Branch
^^^^^^^^^^^^^^^

Always create a new branch for your changes. Choose a descriptive name for the branch based on the feature or fix you're working on:

.. code-block:: bash

   git checkout -b feature/my-feature-name

Write Your Code
^^^^^^^^^^^^^^^

- Add or modify functionality in the appropriate module.
- Ensure your code follows the `Code Style <#code-style>`_ guidelines.
- Write or update tests for your changes.

Run Tests
^^^^^^^^^

Before submitting your contribution, run the test suite to ensure your changes don't break existing functionality:

.. code-block:: bash

   pytest tests/test_*.py
   # or simply
   pytest

If you're adding new functionality, be sure to include tests to cover that behavior.

Submit a Pull Request
^^^^^^^^^^^^^^^^^^^^^

Once you're ready to submit your changes:

1. Push the changes to your branch on your forked repository:

   .. code-block:: bash

      git push origin feature/my-feature-name

2. Open a pull request (PR) from your fork to the original repository. In your PR description:
   - Explain the purpose of the changes.
   - Link to the relevant issue if it exists.
   - Provide any additional context or background for reviewers.

Code Style
----------

We follow `PEP 8 <https://pep8.org/>`_ for Python code style. Please ensure your code adheres to these guidelines. Additionally, we use the following tools to maintain code quality:

- **Black** for code formatting:

  .. code-block:: bash

     black .

Testing
-------

We use the ``pytest`` framework for testing. Please ensure that all new features and changes are covered by unit tests.

To run the test suite:

.. code-block:: bash

   pytest

You are encouraged to write tests that cover edge cases and typical usage patterns. All tests should pass before you submit a pull request.

Documentation
-------------

Documentation is important! If you make changes to the codebase, please ensure the relevant documentation is updated. Documentation is currently provided as part of the main `README.rst <./README.rst>`_

- Ensure all public methods, functions, and classes are well-documented with docstrings.
- If adding a new feature or CLI command, update the README or other relevant documentation.

License
-------

By contributing to this project, you agree that your contributions will be licensed under the `Apache License 2.0 <./LICENSE>`_.

Thank you for your contributions!
