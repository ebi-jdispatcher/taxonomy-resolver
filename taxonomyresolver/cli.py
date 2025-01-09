#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2024.
:license: Apache 2.0, see LICENSE for more details.
"""

import click

from taxonomyresolver import TaxonResolver, __version__
from taxonomyresolver.utils import (
    load_logging,
    parse_tax_ids,
    print_and_exit,
    validate_inputs_outputs,
)
from taxonomyresolver.tree import write_tree


# reusing click args and options
def add_common(options: list):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


common_options = [
    click.option(
        "-level",
        "--log_level",
        "log_level",
        type=str,
        default="INFO",
        multiple=False,
        help="Log level to use. Expects: 'DEBUG', 'INFO',"
        " 'WARN', 'ERROR', and 'CRITICAL'.",
    ),
    click.option(
        "-l",
        "--log_output",
        "log_output",
        type=str,
        required=False,
        multiple=False,
        help="File name to be used to writing logging.",
    ),
    click.option(
        "--quiet",
        "quiet",
        is_flag=True,
        default=False,
        multiple=False,
        help="Disables logging.",
    ),
]

common_options_parsing = [
    click.option(
        "-sep",
        "--sep",
        "sep",
        type=str,
        required=False,
        default=None,
        multiple=False,
        help="String Separator to use.",
    ),
    click.option(
        "-indx",
        "--indx",
        "indx",
        type=int,
        required=False,
        default=0,
        multiple=False,
        help="String positional index to use (starts with 0).",
    ),
]


@click.group(chain=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
def cli():
    """Taxonomy Resolver: Build a NCBI Taxonomy Tree, validate and search TaxIDs."""
    pass


@cli.command("download")
@click.option(
    "-out",
    "--outfile",
    "outfile",
    is_flag=False,
    type=str,
    required=True,
    multiple=False,
    help="Path to output Tax dump file.",
)
@click.option(
    "-outf",
    "--outformat",
    "outformat",
    type=str,
    default="zip",
    required=False,
    multiple=False,
    help="Output format (currently: 'zip' or 'tar.gz').",
)
@add_common(common_options)
def download(
    outfile: str,
    outformat: str,
    log_level: str = "INFO",
    log_output: str | None = None,
    quiet: bool = False,
):
    """Download the NCBI Taxonomy dump file ('taxdmp.zip')."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(outputfile=outfile)
    logging.info("Validated output.")

    resolver = TaxonResolver(logging)
    resolver.download(outfile, outformat)
    logging.info("Downloaded NCBI Taxonomy Dump from FTP.")


@cli.command("build")
@click.option(
    "-in",
    "--infile",
    "infile",
    is_flag=False,
    type=str,
    required=True,
    multiple=False,
    help=(
        "Path to input NCBI BLAST dump or a prebuilt tree file, "
        "(currently: 'pickle')."
    ),
)
@click.option(
    "-out",
    "--outfile",
    "outfile",
    is_flag=False,
    type=str,
    required=True,
    multiple=False,
    help="Path to output file.",
)
@click.option(
    "-inf",
    "--informat",
    "informat",
    type=str,
    default=None,
    required=False,
    multiple=False,
    help="Input format (currently: 'pickle').",
)
@click.option(
    "-outf",
    "--outformat",
    "outformat",
    type=str,
    default="pickle",
    required=False,
    multiple=False,
    help="Output format (currently: 'pickle' or 'newick').",
)
@click.option(
    "-taxidsf",
    "--taxidfilter",
    "taxidfilters",
    type=str,
    required=False,
    multiple=True,
    help="Path to Taxonomy id list file used to filter the search.",
)
@click.option(
    "-ignore",
    "--ignoreinvalid",
    "ignoreinvalid",
    is_flag=True,
    default=False,
    multiple=False,
    help="Ignores invalid TaxIDs.",
)
@click.option(
    "-slim",
    "--slimtable",
    "slimtable",
    is_flag=True,
    default=False,
    multiple=False,
    help="Drops unnecessary columns from the pandas DataFrame.",
)
@add_common(common_options)
@add_common(common_options_parsing)
def build(
    infile: str,
    outfile: str,
    informat: str | None,
    outformat: str,
    taxidfilters: tuple | None = None,
    ignoreinvalid: bool = False,
    sep: str | None = None,
    indx: int = 0,
    slimtable: bool = False,
    log_level: str = "INFO",
    log_output: str | None = None,
    quiet: bool = False,
):
    """Build a NCBI Taxonomy Tree data structure."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    validate_inputs_outputs(inputfile=infile, outputfile=outfile)
    if taxidfilters:
        for taxidfilter in taxidfilters:
            validate_inputs_outputs(inputfile=taxidfilter)
    logging.info("Validated inputs and outputs.")

    resolver = TaxonResolver(logging)
    if informat:
        resolver.load(infile, informat)
        logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")
    else:
        logging.info(
            f"Building NCBI Taxonomy from {infile}. "
            f"This may take several minutes to complete..."
        )
        resolver.build(infile)
        logging.info(f"Built NCBI Taxonomy from {infile}.")
    if taxidfilters:
        filterids = []
        for taxidfilter in taxidfilters:
            filterids.extend(parse_tax_ids(taxidfilter, sep=sep, indx=indx))
        resolver.filter(taxidfilter=filterids, ignoreinvalid=ignoreinvalid)
        logging.info(f"Filtered NCBI Taxonomy with the provided filters.")

    # dropping unnecessary columns
    if slimtable and resolver.tree:
        resolver.tree.drop(["rank", "depth", "parent_id"], axis=1, inplace=True)
    resolver.write(outfile, outformat)
    logging.info(f"Wrote NCBI Taxonomy tree {outfile} in {outformat} format.")


@cli.command("search")
@click.option(
    "-in",
    "--infile",
    "infile",
    is_flag=False,
    type=str,
    required=True,
    multiple=False,
    help=(
        "Path to input NCBI BLAST dump or a prebuilt tree file, "
        "(currently: 'pickle')."
    ),
)
@click.option(
    "-out",
    "--outfile",
    "outfile",
    is_flag=False,
    type=str,
    required=False,
    multiple=False,
    help="Path to output file.",
)
@click.option(
    "-inf",
    "--informat",
    "informat",
    type=str,
    default="pickle",
    required=False,
    multiple=False,
    help="Input format (currently: 'pickle').",
)
@click.option(
    "-outf",
    "--outformat",
    "outformat",
    type=str,
    default="txt",
    required=False,
    multiple=False,
    help="Input format (currently: 'txt' or 'newick').",
)
@click.option(
    "-taxid",
    "--taxid",
    "taxids",
    is_flag=False,
    type=str,
    required=False,
    multiple=True,
    help=(
        "Comma-separated TaxIDs or pass multiple values. Output to "
        "STDOUT by default, unless an output file is provided."
    ),
)
@click.option(
    "-taxids",
    "--taxidinclude",
    "taxidincludes",
    type=str,
    required=False,
    multiple=True,
    help="Path to Taxonomy id list file used to search the Tree.",
)
@click.option(
    "-taxidexc",
    "--taxidexc",
    "taxidsexcludes",
    is_flag=False,
    type=str,
    required=False,
    multiple=True,
    help="Comma-separated TaxIDs or pass multiple values.",
)
@click.option(
    "-taxidse",
    "--taxidexclude",
    "taxidexcludes",
    type=str,
    required=False,
    multiple=True,
    help="Path to Taxonomy id list file excluded from the search.",
)
@click.option(
    "-taxidsf",
    "--taxidfilter",
    "taxidfilters",
    type=str,
    required=False,
    multiple=True,
    help="Path to Taxonomy id list file used to filter the search.",
)
@click.option(
    "-ignore",
    "--ignoreinvalid",
    "ignoreinvalid",
    is_flag=True,
    default=False,
    multiple=False,
    help="Ignores invalid TaxIDs.",
)
@add_common(common_options)
@add_common(common_options_parsing)
def search(
    infile: str,
    outfile: str | None,
    informat: str,
    outformat: str,
    taxids: str | None,
    taxidincludes: str | None,
    taxidsexcludes: str | None,
    taxidexcludes: str | None,
    taxidfilters: tuple | None = None,
    ignoreinvalid: bool = False,
    sep: str | None = None,
    indx: int = 0,
    log_level: str = "INFO",
    log_output: str | None = None,
    quiet: bool = False,
):
    """Searches a Tree data structure and writes a list of TaxIDs."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    if not taxids and not taxidincludes:
        print_and_exit(f"TaxIDs need to be provided to execute a search!")

    validate_inputs_outputs(inputfile=infile)
    if outfile:
        validate_inputs_outputs(outputfile=outfile)
    if taxidincludes:
        for taxidinclude in taxidincludes:
            validate_inputs_outputs(inputfile=taxidinclude)
    if taxidexcludes:
        for taxidexclude in taxidexcludes:
            validate_inputs_outputs(inputfile=taxidexclude)
    if taxidfilters:
        for taxidfilter in taxidfilters:
            validate_inputs_outputs(inputfile=taxidfilter)
    logging.info("Validated inputs and outputs.")

    resolver = TaxonResolver(logging)
    resolver.load(infile, informat)
    logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")

    includeids = []
    if taxidincludes:
        for taxidinclude in taxidincludes:
            includeids.extend(parse_tax_ids(taxidinclude))
    else:
        if taxids:
            for taxid in taxids:
                includeids.extend(taxid.split(","))

    excludeids = []
    if taxidexcludes:
        for taxidexclude in taxidexcludes:
            excludeids.extend(parse_tax_ids(taxidexclude))
    elif taxidsexcludes:
        for taxid in taxidsexcludes:
            excludeids.extend(taxid.split(","))

    filterids = []
    if taxidfilters:
        for taxidfilter in taxidfilters:
            filterids.extend(parse_tax_ids(taxidfilter, sep=sep, indx=indx))

    tax_ids = resolver.search(
        taxidinclude=includeids,
        taxidexclude=excludeids,
        taxidfilter=filterids,
        ignoreinvalid=ignoreinvalid,
    )
    if outfile:
        if outformat == "newick" and resolver.tree is not None and tax_ids:
            subset = (
                resolver.tree[resolver.tree["id"].isin(list(tax_ids))]
                .sort_values("lft")
                .reset_index()
            )
            write_tree(subset, outputfile=outfile, outputformat=outformat)
        else:
            with open(outfile, "w") as outf:
                if tax_ids:
                    outf.write("\n".join(list(tax_ids)))
        logging.info(f"Wrote list of TaxIDS in {outfile} in '{outformat}' format.")
    else:
        try:
            if tax_ids:
                print(",".join(tax_ids))
        except TypeError:
            print(tax_ids)


@cli.command("validate")
@click.option(
    "-in",
    "--infile",
    "infile",
    is_flag=False,
    type=str,
    required=True,
    multiple=False,
    help=(
        "Path to input NCBI BLAST dump or a prebuilt tree file, "
        "(currently: 'pickle')."
    ),
)
@click.option(
    "-inf",
    "--informat",
    "informat",
    type=str,
    default="pickle",
    required=False,
    multiple=False,
    help="Input format (currently: 'pickle').",
)
@click.option(
    "-taxid",
    "--taxid",
    "taxids",
    is_flag=False,
    type=str,
    required=False,
    multiple=True,
    help="Comma-separated TaxIDs or pass multiple values. Output to "
    "STDOUT by default.",
)
@click.option(
    "-taxids",
    "--taxidinclude",
    "taxidincludes",
    type=str,
    required=False,
    multiple=True,
    help="Path to Taxonomy id list file used to search the Tree.",
)
@add_common(common_options)
def validate(
    infile: str,
    informat: str,
    taxids: str | None,
    taxidincludes: str | None,
    log_level: str = "INFO",
    log_output: str | None = None,
    quiet: bool = False,
):
    """Validates a list of TaxIDs against a Tree data structure."""

    logging = load_logging(log_level, log_output, disabled=quiet)

    # input options validation
    if not taxids and not taxidincludes:
        print_and_exit(f"TaxIDs need to be provided to execute a search!")

    validate_inputs_outputs(inputfile=infile)
    if taxidincludes:
        for taxidinclude in taxidincludes:
            validate_inputs_outputs(inputfile=taxidinclude)
    logging.info("Validated inputs.")

    resolver = TaxonResolver(logging)
    resolver.load(infile, informat)
    logging.info(f"Loaded NCBI Taxonomy from '{infile}' in '{informat}' format.")

    if taxidincludes:
        includeids = []
        for taxidinclude in taxidincludes:
            includeids.extend(parse_tax_ids(taxidinclude))
    else:
        includeids = []
        if taxids:
            for taxid in taxids:
                includeids.extend(taxid.split(","))
    valid = resolver.validate(taxidinclude=includeids)
    logging.info(f"Validated TaxIDs in the '{infile}' tree.")
    print_and_exit(str(valid))


if __name__ == "__main__":
    cli()
