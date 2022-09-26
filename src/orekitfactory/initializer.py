"""Load default data and initialize orekit."""
import orekit
import orekit.pyhelpers
import os.path

from .utils import Dataloader

vm = None


def get_orekit_vm():
    """Get the reference to a singleton orekit vm.

    This method will create the vm if not otherwise set

    Returns:
        Any: A reference to the running orekit java vm
    """
    global vm
    if not vm:
        vm = orekit.initVM()
    return vm


def init_orekit(
    source: str = "https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip",  # noqa: E501
):
    """Initialize orekit with the data source, downloading the data if necessary.

    The data is loaded into the `Dataloader.data_dir` Set that value prior to calling
    this method to adjust.

    Args:
        source (str, optional): The data source, may be a file, directory, or url.
        Defaults to
        "https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip".

    """
    if os.path.exists(source):
        orekit_data_file = source
    else:
        orekit_data_file = Dataloader.download(source)

    orekit.pyhelpers.setup_orekit_curdir(filename=orekit_data_file)
