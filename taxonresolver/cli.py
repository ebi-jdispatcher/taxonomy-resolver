#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import click

from taxonresolver import __version__

from taxonresolver import TaxonResolver
from taxonresolver import TaxonResolverFast
from taxonresolver.utils import load_logging
from taxonresolver.utils import print_and_exit
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

common_options_mode = [
    click.option('-mode', '--mode', 'mode', type=str, required=False, default="anytree",
                 multiple=False, help="Usage mode (currently 'anytree' or 'fast').")
]


@click.group(chain=True, context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__version__)
def cli():
    """Taxonomy Resolver: Build NCBI Taxonomy Trees and lists of TaxIDs."""
    pass


@cli.command("download")
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=True,
              multiple=False, help="Path to output Tax dump file.")
@click.option('-outf', '--outformat', 'outformat', type=str, default="zip", required=False,
              multiple=False, help="Output format (currently: 'zip' or 'tar.gz').")
@add_common(common_options)
def download(outfile: str, outformat: str,
             log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Download the NCBI Taxonomy dump file."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(outputfile=outfile)
    logging.info("Validated output.")

    resolver = TaxonResolver(logging)
    resolver.download(outfile, outformat)
    logging.info("Downloaded NCBI Taxonomy Dump from FTP.")


@cli.command("build")
@click.option('-in', '--infile', 'infile', is_flag=False, type=str, required=True,
              multiple=False, help=("Path to input NCBI BLAST dump or a prebuilt tree file, "
                                    "(currently: 'json' or 'pickle')."))
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=True,
              multiple=False, help="Path to output file.")
@click.option('-inf', '--informat', 'informat', type=str, default=None, required=False,
              multiple=False, help="Input format (currently: 'json' or 'pickle').")
@click.option('-outf', '--outformat', 'outformat', type=str, default="json", required=True,
              multiple=False, help="Output format (currently: 'json' or 'pickle').")
@click.option('-taxidf', '--taxidfilter', 'taxidfilter', type=str, required=False,
              multiple=False, help="Path to Taxonomy id list file used to filter the Tree.")
@add_common(common_options)
@add_common(common_options_mode)
def build(infile: str, outfile: str, informat: str or None, outformat: str,
          taxidfilter: str, mode: str = "anytree",
          log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Build NCBI Taxonomy Tree in JSON or Pickle."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(inputfile=infile, outputfile=outfile)
    if taxidfilter:
        validate_inputs_outputs(inputfile=taxidfilter)
    logging.info("Validated inputs and outputs.")

    if mode == "anytree":
        resolver = TaxonResolver(logging)
        if informat:
            resolver.load(infile, informat)
            logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")
        else:
            logging.info(f"Building NCBI Taxonomy from {infile}. "
                         f"This can take several minutes to complete...")
            resolver.build(infile)
            logging.info(f"Built NCBI Taxonomy from {infile}.")

        if taxidfilter:
            resolver.filter(taxidfilter)
            logging.info(f"Filtered NCBI Taxonomy with {taxidfilter}.")
    elif mode == "fast":
        resolver = TaxonResolverFast(logging)
        logging.info(f"Building NCBI Taxonomy from {infile}... ")
        resolver.build(infile, informat)
        logging.info(f"Built NCBI Taxonomy from {infile}.")
    else:
        print_and_exit(f"Mode '{mode}' is not valid!")

    resolver.write(outfile, outformat)
    logging.info(f"Wrote NCBI Taxonomy tree {outfile} in {outformat} format.")


@cli.command("search")
@click.option('-in', '--infile', 'infile', is_flag=False, type=str, required=True,
              multiple=False, help=("Path to input NCBI BLAST dump or a prebuilt tree file, "
                                    "(currently: 'json' or 'pickle')."))
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=True,
              multiple=False, help="Path to output file.")
@click.option('-inf', '--informat', 'informat', type=str, default="json", required=True,
              multiple=False, help="Input format (currently: 'json' or 'pickle').")
@click.option('-taxids', '--taxidsearch', 'taxidsearch', type=str, required=True,
              multiple=False, help="Path to Taxonomy id list file used to search the Tree.")
@click.option('-taxidf', '--taxidfilter', 'taxidfilter', type=str, required=False,
              multiple=False, help="Path to Taxonomy id list file used to filter the Tree.")
@add_common(common_options)
@add_common(common_options_mode)
def search(infile: str, outfile: str, informat: str, taxidsearch: str,
           taxidfilter: str = None, mode: str = "anytree",
           log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Searches a NCBI Taxonomy Tree and writes a list of TaxIDs."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(inputfile=infile, outputfile=outfile)
    validate_inputs_outputs(inputfile=taxidsearch)
    if taxidfilter:
        validate_inputs_outputs(inputfile=taxidfilter)
    logging.info("Validated inputs and outputs.")

    if mode == "anytree":
        resolver = TaxonResolver(logging)
    elif mode == "fast":
        resolver = TaxonResolverFast(logging)
    else:
        print_and_exit(f"Mode '{mode}' is not valid!")

    resolver.load(infile, informat)
    logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")

    tax_ids = resolver.search(taxidsearch, taxidfilter)
    with open(outfile, "w") as outfile:
        outfile.write("\n".join(tax_ids))
    logging.info(f"Wrote list of TaxIDS in {outfile}.")


@cli.command("validate")
@click.option('-in', '--infile', 'infile', is_flag=False, type=str, required=True,
              multiple=False, help=("Path to input NCBI BLAST dump or a prebuilt tree file, "
                                    "(currently: 'json' or 'pickle')."))
@click.option('-inf', '--informat', 'informat', type=str, default="json", required=True,
              multiple=False, help="Input format (currently: 'json' or 'pickle').")
@click.option('-taxids', '--taxidsearch', 'taxidsearch', type=str, required=True,
              multiple=False, help="Path to Taxonomy id list file used to search the Tree.")
@click.option('-taxidf', '--taxidfilter', 'taxidfilter', type=str, required=False,
              multiple=False, help="Path to Taxonomy id list file used to filter the Tree.")
@add_common(common_options)
@add_common(common_options_mode)
def validate(infile: str, informat: str, taxidsearch: str,
             taxidfilter: str = None, mode: str = "anytree",
             log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Validates a list of TaxIDs against a NCBI Taxonomy Tree."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(inputfile=infile)
    validate_inputs_outputs(inputfile=taxidsearch)
    if taxidfilter:
        validate_inputs_outputs(inputfile=taxidfilter)
    logging.info("Validated inputs.")

    if mode == "anytree":
        resolver = TaxonResolver(logging)
    elif mode == "fast":
        resolver = TaxonResolverFast(logging)
    else:
        print_and_exit(f"Mode '{mode}' is not valid!")

    resolver.load(infile, informat)
    logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")

    valid = resolver.validate(taxidsearch, taxidfilter)
    logging.info(f"Validated TaxIDs from '{taxidsearch}' in the '{infile}' tree.")
    print_and_exit(str(valid))


if __name__ == '__main__':
    cli()
