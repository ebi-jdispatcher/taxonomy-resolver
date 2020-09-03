#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
import sys
import requests
import logging

from anytree import NodeMixin


class ReadOnlyError(RuntimeError):
    pass


def _repr(node, args=None, nameblacklist=None):
    classname = node.__class__.__name__
    args = args or []
    nameblacklist = nameblacklist or []
    for key, value in filter(lambda item:
                             not item[0].startswith("_") and item[0] not in nameblacklist,
                             sorted(node.__dict__.items(),
                                    key=lambda item: item[0])):
        args.append("%s=%r" % (key, value))
    return "%s(%s)" % (classname, ", ".join(args))


class Node(NodeMixin, object):

    def __init__(self, name, parent=None, children=None, **kwargs):
        u"""
        A simple tree node with a `name` and any `kwargs`.
        Edit: Modified to be read-only by default.

        Args:
            name: A name or any other object this node can reference to as idendifier.

        Keyword Args:
            parent: Reference to parent node.
            children: Iterable with child nodes.
            *: Any other given attribute is just stored as object attribute.

        Other than :any:`AnyNode` this class has at least the `name` attribute,
        to distinguish between different instances.

        The `parent` attribute refers the parent node:

        >>> from anytree import Node, RenderTree
        >>> root = Node("root")
        >>> s0 = Node("sub0", parent=root)
        >>> s0b = Node("sub0B", parent=s0, foo=4, bar=109)
        >>> s0a = Node("sub0A", parent=s0)
        >>> s1 = Node("sub1", parent=root)
        >>> s1a = Node("sub1A", parent=s1)
        >>> s1b = Node("sub1B", parent=s1, bar=8)
        >>> s1c = Node("sub1C", parent=s1)
        >>> s1ca = Node("sub1Ca", parent=s1c)

        >>> print(RenderTree(root))
        Node('/root')
        ├── Node('/root/sub0')
        │   ├── Node('/root/sub0/sub0B', bar=109, foo=4)
        │   └── Node('/root/sub0/sub0A')
        └── Node('/root/sub1')
            ├── Node('/root/sub1/sub1A')
            ├── Node('/root/sub1/sub1B', bar=8)
            └── Node('/root/sub1/sub1C')
                └── Node('/root/sub1/sub1C/sub1Ca')

        The same tree can be constructed by using the `children` attribute:

        >>> root = Node("root", children=[
        ...     Node("sub0", children=[
        ...         Node("sub0B", bar=109, foo=4),
        ...         Node("sub0A", children=None),
        ...     ]),
        ...     Node("sub1", children=[
        ...         Node("sub1A"),
        ...         Node("sub1B", bar=8, children=[]),
        ...         Node("sub1C", children=[
        ...             Node("sub1Ca"),
        ...         ]),
        ...     ]),
        ... ])

        >>> print(RenderTree(root))
        Node('/root')
        ├── Node('/root/sub0')
        │   ├── Node('/root/sub0/sub0B', bar=109, foo=4)
        │   └── Node('/root/sub0/sub0A')
        └── Node('/root/sub1')
            ├── Node('/root/sub1/sub1A')
            ├── Node('/root/sub1/sub1B', bar=8)
            └── Node('/root/sub1/sub1C')
                └── Node('/root/sub1/sub1C/sub1Ca')
        """
        super(Node, self).__init__()
        self.__readonly = False
        self.__dict__.update(kwargs)
        self.name = name
        self.parent = parent
        if children:
            self.children = children
        self.readonly = False

    def _pre_attach(self, parent):
        if self.__readonly:
            raise ReadOnlyError()

    def _pre_detach(self, parent):
        raise ReadOnlyError()

    def __repr__(self):
        args = ["%r" % self.separator.join([""] + [str(node.name) for node in self.path])]
        return _repr(self, args=args, nameblacklist=["name"])


def get_logging_level(level: str = 'INFO') -> logging:
    if level == 'DEBUG':
        return logging.DEBUG
    elif level == 'INFO':
        return logging.INFO
    elif level == 'WARN':
        return logging.WARN
    elif level == 'ERROR':
        return logging.ERROR
    elif level == 'CRITICAL':
        return logging.CRITICAL
    else:
        return logging.INFO


def load_logging(log_level: str, log_output: str = None, disabled: bool = False) -> logging:
    logging.basicConfig(format='%(asctime)s - [%(levelname)s] %(message)s',
                        level=get_logging_level(log_level),
                        datefmt='%d/%m/%Y %H:%M:%S')
    if log_output:
        file_handler = logging.FileHandler(log_output)
        logging.getLogger().addHandler(file_handler)

    if disabled:
        logging.disable(100)
    logging.debug(f"Logging level set to {log_level}")
    return logging


def print_and_exit(message: str) -> None:
    print(message)
    sys.exit()


def validate_inputs_outputs(inputfile: str or None = None,
                            outputfile: str or None = None) -> None:
    """
    Checks if the passed input/output files are valid and exist.

    :param inputfile: input file paths
    :param outputfile: output file paths
    :return: (side-effects)
    """

    if inputfile:
        if not os.path.isfile(inputfile):
            print_and_exit(f"Input file '{inputfile}' does not exist or it is not readable!")

    if outputfile:
        try:
            open(outputfile, "a").close()
        except IOError:
            print_and_exit(f"Output file '{outputfile}' cannot be opened or created!")


def download_taxonomy_dump(outfile, extension="zip") -> None:
    """
    Download Taxonomy Dump file from NCBI Taxonomy FTP server.

    :param outfile: Path to output file
    :param extension: (str) "zip" or "tar.gz"
    :return: (side-effects) writes file
    """

    if extension == "zip":
        url = "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdmp.zip"
    else:
        url = "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"
    r = requests.get(url, allow_redirects=True)
    if r.ok:
        open(outfile, 'wb').write(r.content)
    else:
        print(f"Unable to Download Taxonomy Dump from {url}")


def escape_literal(text) -> str:
    return text.replace('"', '\\"')


def label_to_id(text) -> str:
    return text.replace(" ", "_").replace("-", "_")


def split_line(line) -> list:
    """Split a line from a dmp file"""
    return [x.strip() for x in line.split("	|")]


def parse_tax_ids(inputfile: str, sep: str or None = " ", indx: int = 0) -> list:
    """
    Parses a list of TaxIDs from an input file.
    It skips lines started with '#'.

    :param inputfile: Path to inputfile, which is a list of
        Taxonomy Identifiers
    :param sep: separator for splitting the input file lines
    :param indx: index used for splicing the the resulting list
    :return: list of TaxIDs
    """
    tax_ids = []
    with open(inputfile, "r") as infile:
        for line in infile:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            if line != "":
                if sep:
                    tax_id = line.split(sep)[indx]
                else:
                    tax_id = line.split()[indx]
                if tax_id != "":
                    tax_ids.append(tax_id)
    return tax_ids
