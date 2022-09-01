"""Unit tests for the initializer."""
from unittest.mock import patch

import orekitfactory.initializer


@patch("orekitfactory.initializer.Dataloader.download")
@patch("orekitfactory.initializer.orekit.pyhelpers.setup_orekit_curdir")
@patch("orekitfactory.initializer.orekit.initVM")
def test_initialize(mock_orekit, mock_pyhelpers, mock_dataloader):
    mock_dataloader.return_value = ["/path/to/orekit-data.zip"]

    orekitfactory.initializer.init_orekit()

    args, kwargs = mock_pyhelpers.call_args

    assert "/path/to/orekit-data.zip" == kwargs["filename"][0]
