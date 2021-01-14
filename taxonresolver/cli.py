#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2021.
:license: Apache 2.0, see LICENSE for more details.
"""

import click

from taxonresolver import __version__

from taxonresolver import TaxonResolver
from taxonresolver.utils import load_logging
from taxonresolver.utils import print_and_exit
from taxonresolver.utils import parse_tax_ids
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

common_options_parsing = [
    click.option('-sep', '--sep', 'sep', type=str, required=False, default=None,
                 multiple=False, help="String Separator to use."),
    click.option('-indx', '--indx', 'indx', type=int, required=False, default=0,
                 multiple=False, help="String positional index to use (starts with 0).")
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
                                    "(currently: 'pickle')."))
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=True,
              multiple=False, help="Path to output file.")
@click.option('-inf', '--informat', 'informat', type=str, default=None, required=False,
              multiple=False, help="Input format (currently: 'pickle').")
@click.option('-outf', '--outformat', 'outformat', type=str, default="pickle", required=True,
              multiple=False, help="Output format (currently: 'pickle').")
@add_common(common_options)
def build(infile: str, outfile: str, informat: str or None, outformat: str,
          log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Build NCBI Taxonomy Tree in JSON or Pickle."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(inputfile=infile, outputfile=outfile)
    logging.info("Validated inputs and outputs.")

    resolver = TaxonResolver(logging)
    if informat:
        resolver.load(infile, informat)
        logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")
    else:
        logging.info(f"Building NCBI Taxonomy from {infile}. "
                     f"This may take several minutes to complete...")
        resolver.build(infile)
        logging.info(f"Built NCBI Taxonomy from {infile}.")

    resolver.write(outfile, outformat)
    logging.info(f"Wrote NCBI Taxonomy tree {outfile} in {outformat} format.")


@cli.command("search")
@click.option('-in', '--infile', 'infile', is_flag=False, type=str, required=True,
              multiple=False, help=("Path to input NCBI BLAST dump or a prebuilt tree file, "
                                    "(currently: 'pickle')."))
@click.option('-out', '--outfile', 'outfile', is_flag=False, type=str, required=False,
              multiple=False, help="Path to output file.")
@click.option('-inf', '--informat', 'informat', type=str, default="pickle", required=True,
              multiple=False, help="Input format (currently: 'pickle').")
@click.option('-taxid', '--taxid', 'taxid', is_flag=False, type=str, required=False,
              multiple=False, help=("Comma-separated TaxIDs. Output to STDOUT by default, "
                                    "unless an output file is provided."))
@click.option('-taxids', '--taxidsearch', 'taxidsearch', type=str, required=False,
              multiple=False, help="Path to Taxonomy id list file used to search the Tree.")
@click.option('-taxidf', '--taxidfilter', 'taxidfilters', type=str, required=False,
              multiple=True, help="Path to Taxonomy id list file used to filter the Tree.")
@add_common(common_options)
@add_common(common_options_parsing)
def search(infile: str, outfile: str or None, informat: str,
           taxid: str or None, taxidsearch: str or None,
           taxidfilters: tuple = None, sep: str = None, indx: int = 0,
           log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Searches a NCBI Taxonomy Tree and writes a list of TaxIDs."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    if not taxid and not taxidsearch:
        print_and_exit(f"TaxIDs need to be provided to execute a search!")

    validate_inputs_outputs(inputfile=infile)
    if outfile:
        validate_inputs_outputs(outputfile=outfile)
    if taxidsearch:
        validate_inputs_outputs(inputfile=taxidsearch)
    if taxidfilters:
        for taxidfilter in taxidfilters:
            validate_inputs_outputs(inputfile=taxidfilter)
    logging.info("Validated inputs and outputs.")

    resolver = TaxonResolver(logging)
    resolver.load(infile, informat)
    logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")

    taxidfilterids = []
    if taxidfilters:
        for taxidfilter in taxidfilters:
            taxidfilterids.extend(parse_tax_ids(taxidfilter, sep=sep, indx=indx))

    if taxidsearch:
        searchids = taxidsearch
    else:
        searchids = list(set(taxid.split(",")))
    tax_ids = resolver.search(searchids, list(set(taxidfilterids)))
    if outfile:
        with open(outfile, "w") as outfile:
            outfile.write("\n".join(tax_ids))
    else:
        try:
            print(",".join(tax_ids))
        except TypeError:
            print(tax_ids)
    logging.info(f"Wrote list of TaxIDS in {outfile}.")


@cli.command("validate")
@click.option('-in', '--infile', 'infile', is_flag=False, type=str, required=True,
              multiple=False, help=("Path to input NCBI BLAST dump or a prebuilt tree file, "
                                    "(currently: 'pickle')."))
@click.option('-inf', '--informat', 'informat', type=str, default="pickle", required=True,
              multiple=False, help="Input format (currently: 'pickle').")
@click.option('-taxid', '--taxid', 'taxid', is_flag=False, type=str, required=False,
              multiple=False, help="Comma-separated TaxIDs. Output to STDOUT by default.")
@click.option('-taxids', '--taxidsearch', 'taxidsearch', type=str, required=False,
              multiple=False, help="Path to Taxonomy id list file used to search the Tree.")
@add_common(common_options)
def validate(infile: str, informat: str,
             taxid: str or None, taxidsearch: str or None,
             log_level: str = "INFO", log_output: str = None, quiet: bool = False):
    """Validates a list of TaxIDs against a NCBI Taxonomy Tree."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    if not taxid and not taxidsearch:
        print_and_exit(f"TaxIDs need to be provided to execute a search!")

    validate_inputs_outputs(inputfile=infile)
    if taxidsearch:
        validate_inputs_outputs(inputfile=taxidsearch)
    logging.info("Validated inputs.")

    resolver = TaxonResolver(logging)
    resolver.load(infile, informat)
    logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")

    if taxidsearch:
        searchids = taxidsearch
    else:
        searchids = list(set(taxid.split(",")))
    valid = resolver.validate(searchids)
    logging.info(f"Validated TaxIDs from '{taxidsearch}' in the '{infile}' tree.")
    print_and_exit(str(valid))


if __name__ == '__main__':
    cli()
