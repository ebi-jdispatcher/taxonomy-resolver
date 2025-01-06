#!/usr/bin/env python
# -*- coding: utf-8

"""
Taxonomy Resolver

:copyright: (c) 2020-2025.
:license: Apache 2.0, see LICENSE for more details.
"""

import os

import click
import pytest
from click.testing import CliRunner

from taxonomyresolver import __version__
from taxonomyresolver.cli import add_common, cli, common_options, common_options_parsing
from taxonomyresolver.utils import load_logging


@pytest.fixture
def context():
    return load_logging("INFO")


@pytest.fixture
def cwd():
    if not os.getcwd().endswith("tests"):
        os.chdir(os.path.join(os.getcwd(), "tests"))
    return os.getcwd()


@pytest.fixture
def runner():
    return CliRunner()


@click.command()
@add_common(common_options)
@add_common(common_options_parsing)
def demo_cli_common_options(log_level, log_output, quiet, sep, indx):
    """A sample command to test 'add_common' decoration and 'common_options'."""
    click.echo(
        f"log_level={log_level}, log_output={log_output}, quiet={quiet}, "
        f"sep={sep}, indx={indx}"
    )


def test_default_behavior(runner):
    """Test the default behavior with no options passed."""
    result = runner.invoke(demo_cli_common_options)
    assert result.exit_code == 0
    assert "log_level=INFO" in result.output
    assert "log_output=None" in result.output
    assert "quiet=False" in result.output
    assert "sep=None" in result.output
    assert "indx=0" in result.output


def test_log_level_option(runner):
    """Test setting the log_level option."""
    result = runner.invoke(demo_cli_common_options, ["--log_level", "DEBUG"])
    assert result.exit_code == 0
    assert "log_level=DEBUG" in result.output


def test_log_output_option(runner):
    """Test setting the log_output option."""
    result = runner.invoke(demo_cli_common_options, ["--log_output", "log.txt"])
    assert result.exit_code == 0
    assert "log_output=log.txt" in result.output


def test_quiet_flag(runner):
    """Test enabling the quiet flag."""
    result = runner.invoke(demo_cli_common_options, ["--quiet"])
    assert result.exit_code == 0
    assert "quiet=True" in result.output


def test_setting_sep(runner):
    """Test setting sep."""
    result = runner.invoke(demo_cli_common_options, ["--sep", "test"])
    assert result.exit_code == 0
    assert "sep=test" in result.output


def test_setting_indx(runner):
    """Test setting indx."""
    result = runner.invoke(demo_cli_common_options, ["--indx", "1"])
    assert result.exit_code == 0
    assert "indx=1" in result.output


def test_combined_options(runner):
    """Test multiple options together."""
    result = runner.invoke(
        demo_cli_common_options,
        ["--log_level", "ERROR", "--log_output", "error.log", "--quiet"],
    )
    assert result.exit_code == 0
    assert "log_level=ERROR" in result.output
    assert "log_output=error.log" in result.output
    assert "quiet=True" in result.output


def test_cli_help(runner):
    """Test the CLI group help message."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Taxonomy Resolver" in result.output
    assert "Build a NCBI Taxonomy Tree" in result.output

    result = runner.invoke(cli, ["-h"])
    assert result.exit_code == 0
    assert "Taxonomy Resolver" in result.output
    assert "Build a NCBI Taxonomy Tree" in result.output


def test_cli_version(runner):
    """Test the CLI version output."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert f"cli, version {__version__}" in result.output


@pytest.mark.skip(reason="Skip test by default!")
def test_download_taxdmp(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "download",
            "-out",
            os.path.join(cwd, f"../testdata/taxdmp.zip"),
            "-outf",
            "zip",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/taxdmp.zip"))


def test_resolver_build_and_write(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "build",
            "-in",
            os.path.join(cwd, "../testdata/taxdmp.zip"),
            "-inf",
            "zip",
            "-out",
            os.path.join(cwd, "../testdata/tree.pickle"),
            "-outf",
            "pickle",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/tree.pickle"))


def test_resolver_build_and_write_mock(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "build",
            "-in",
            os.path.join(cwd, "../testdata/nodes_mock.dmp"),
            "-out",
            os.path.join(cwd, "../testdata/tree_mock.pickle"),
            "-outf",
            "pickle",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/tree_mock.pickle"))


def test_resolver_build_and_write_mock_command_with_options(runner, cwd):
    """Test the build command with various options."""
    result = runner.invoke(
        cli,
        [
            "build",
            "-in",
            os.path.join(cwd, "../testdata/nodes_mock.dmp"),
            "-out",
            os.path.join(cwd, "../testdata/tree_mock.pickle"),
            "-outf",
            "pickle",
            "--log_level",
            "DEBUG",
            "--log_output",
            "log.txt",
            "--quiet",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/tree_mock.pickle"))


def test_resolver_build_and_write_mock_group_chaining(runner, cwd):
    """Test chaining subcommands in the group."""
    result = runner.invoke(
        cli,
        [
            "build",
            "-in",
            os.path.join(cwd, "../testdata/nodes_mock.dmp"),
            "-out",
            os.path.join(cwd, "../testdata/tree_mock.pickle"),
            "-outf",
            "pickle",
            "--log_level",
            "WARN",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/tree_mock.pickle"))


def test_resolver_and_write_and_filter(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "build",
            "-in",
            os.path.join(cwd, "../testdata/taxdmp.zip"),
            "-inf",
            "zip",
            "-taxidsf",
            os.path.join(cwd, "../testdata/taxids_filter.txt"),
            "-out",
            os.path.join(cwd, "../testdata/tree_filtered.pickle"),
            "-outf",
            "pickle",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/tree_filtered.pickle"))


def test_resolver_load_pickle_and_search_human(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "search",
            "-in",
            os.path.join(cwd, "../testdata/tree_mock.pickle"),
            "-inf",
            "pickle",
            "-taxid",
            "9606",
            "-out",
            os.path.join(cwd, "../testdata/search_human.txt"),
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/search_human.txt"))
    os.remove(os.path.join(cwd, "../testdata/search_human.txt"))


def test_resolver_load_pickle_and_search_mock_include_exclude(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "search",
            "-in",
            os.path.join(cwd, "../testdata/tree_mock.pickle"),
            "-inf",
            "pickle",
            "-taxid",
            "19",
            "-taxids",
            "19,20,21,22,23,24",
            "-taxidexc",
            "24",
            "-out",
            os.path.join(cwd, "../testdata/search_include_exclude.txt"),
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(cwd, "../testdata/search_include_exclude.txt"))
    os.remove(os.path.join(cwd, "../testdata/search_include_exclude.txt"))


def test_resolver_load_pickle_and_validate(runner, cwd):
    result = runner.invoke(
        cli,
        [
            "validate",
            "-in",
            os.path.join(cwd, "../testdata/tree_mock.pickle"),
            "-inf",
            "pickle",
            "-taxid",
            "9606",
        ],
    )
    assert result.exit_code == 0
