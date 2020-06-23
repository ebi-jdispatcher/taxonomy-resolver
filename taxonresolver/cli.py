#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import click

from taxonresolver import __version__

from taxonresolver.tree import TaxonResolver
from taxonresolver.utils import load_logging
from taxonresolver.utils import validate_inputs_outputs


# reusing click args and options
def add_common(options: list):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


common_options = [
    click.option('-level', '--log_level', 'log_level', type=str, default='INFO',
                 multiple=False, help="Log level to use. Expects: 'DEBUG', 'INFO',"
                                      " 'WARN', 'ERROR', and 'CRITICAL'."),
    click.option('-l', '--log_output', 'log_output', type=str, required=False,
                 multiple=False, help="File name to be used to writing logging."),
    click.option('--quiet', 'quiet', is_flag=True, default=False,
                 multiple=False, help="Disables logging.")
]


@click.group(chain=True, context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__version__)
def cli():
    """Taxonomy Resolver: Build NCBI Taxonomy JSON Tree."""
    pass


@click.command("download")
@add_common(common_options)
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=True,
              multiple=False, help="Path to output Tax dump file.")
@click.option('-outformat', '--outformat', 'outformat', type=str, default="json", required=True,
              multiple=False, help="Output format (currently: 'zip' or 'tar.gz').")
def download(outfile: str, outformat: str,
             log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Download the NCBI Taxonomy dump file."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(outputfile=outfile)
    logging.info("Validated inputs and outputs.")

    resolver = TaxonResolver(logging)
    resolver.download(outfile, outformat)
    logging.info("Downloaded NCBI Taxonomy Dump from FTP.")


@click.command("build")
@add_common(common_options)
@click.option('-in', '--infile', 'infile', is_flag=False, type=str, required=True,
              multiple=False, help=("Path to input NCBI BLAST dump or a prebuilt tree file, "
                                    "(currently: 'json' or 'pickle')"))
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=True,
              multiple=False, help="Path to output file.")
@click.option('-informat', '--informat', 'informat', type=str, default="xml", required=True,
              multiple=False, help="Input format (currently: 'json' or 'pickle'")
@click.option('-outformat', '--outformat', 'outformat', type=str, default="json", required=True,
              multiple=False, help="Output format (currently: 'json' or 'pickle').")
def build(infile: str, outfile: str, informat: str, outformat: str,
          log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """TBuild NCBI Taxonomy Tree in JSON or Pickle."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(inputfile=infile, outputfile=outfile)
    logging.info("Validated inputs and outputs.")

    resolver = TaxonResolver(logging)
    if informat:
        tree = resolver.load(infile, informat)
        logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")
    else:
        tree = resolver.build(infile)
        logging.info(f"Built NCBI Taxonomy from {infile}.")

    resolver.write(tree, outfile, outformat)
    logging.info(f"Wrote NCBI Taxonomy tree {outfile} in {outformat} format.")


# TODO
@click.command("search")
@add_common(common_options)
def search(log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    pass


if __name__ == '__main__':
    cli()
