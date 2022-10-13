"""Unit tests for hooks.py."""
import argparse
import pytest
from unittest.mock import patch

import orekitfactory.hooks


def raiseme(*args, **kwargs):
    raise RuntimeError()


def test_pre_init_nullargs():
    """Unit testin verifying default argument parse."""
    orekitfactory.hooks.pre_init(None)


def test_pre_init_noargs():
    """Unit testin verifying default argument parse."""
    parser = argparse.ArgumentParser()

    orekitfactory.hooks.pre_init(parser)

    args = parser.parse_args([])
    assert (
        "https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip"  # noqa: E501
        == args.orekit_data
    )


def test_pre_init_disabled():
    """Unit test verifying argument parsing."""
    try:
        orekitfactory.hooks.ENABLED = False
        parser = argparse.ArgumentParser()

        orekitfactory.hooks.pre_init(parser)

        args = parser.parse_args([])
        assert "orekit_data" not in args

    finally:
        orekitfactory.hooks.ENABLED = True


def test_pre_init_fileargs():
    """Unit test verifying argument parsing."""
    parser = argparse.ArgumentParser()

    orekitfactory.hooks.pre_init(parser)

    args = parser.parse_args(["--orekit-data", __file__])
    assert __file__ == args.orekit_data


def test_pre_init_urlargs():
    """Unit test verifying argument parsing."""
    parser = argparse.ArgumentParser()

    orekitfactory.hooks.pre_init(parser)

    args = parser.parse_args(
        ["--orekit-data", "https://data.pirates.org/yellowbeard.zip"]
    )
    assert "https://data.pirates.org/yellowbeard.zip" == args.orekit_data


@patch("orekitfactory.hooks.get_orekit_vm")
@patch("orekitfactory.hooks.init_orekit")
def test_post_init_noargs(init_orekit, get_vm):
    orekitfactory.hooks.post_init(argparse.Namespace())

    init_orekit.assert_not_called()
    get_vm.assert_called_once()


@patch("orekitfactory.hooks.get_orekit_vm")
@patch("orekitfactory.hooks.init_orekit")
def test_post_init_args(init_orekit, get_vm):
    orekitfactory.hooks.post_init(
        argparse.Namespace(orekit_data="https://pirates.data/yellowbeard.zip")
    )

    init_orekit.assert_called_with(source="https://pirates.data/yellowbeard.zip")
    get_vm.assert_called_once()


@patch("orekitfactory.hooks.get_orekit_vm")
def test_post_init_badvm(get_vm):
    """Unit testin verifying default argument parse."""
    get_vm.side_effect = raiseme

    with pytest.raises(RuntimeError):
        orekitfactory.hooks.post_init(argparse.Namespace())

    get_vm.assert_called_once()


@patch("orekitfactory.hooks.get_orekit_vm")
@patch("orekitfactory.hooks.init_orekit")
def test_post_init_disabled(init_orekit, get_vm):
    try:
        orekitfactory.hooks.ENABLED = False
        orekitfactory.hooks.post_init(
            argparse.Namespace(orekit_data="https://pirates.data/yellowbeard.zip")
        )

        init_orekit.assert_not_called()
        get_vm.assert_not_called()
    finally:
        orekitfactory.hooks.ENABLED = True
