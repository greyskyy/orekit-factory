"""Load default data and initialize orekit."""

import orekit.pyhelpers
from .utils import Dataloader


def init_orekit(
    source: str = "https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip",  # noqa: E501
):
    """Initialize orekit with the data source, downloading the data if necessary.

    The data is loaded into the `Dataloader.data_dir` Set that value prior to calling
    this method to adjust.

    Args:
        source (str, optional): The data source to use. Defaults to
        "https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip".

    """

    orekit_data_file = Dataloader.download(source)
    orekit.pyhelpers.setup_orekit_curdir(filename=orekit_data_file)
