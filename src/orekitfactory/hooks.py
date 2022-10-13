"""py-rebar plugin hooks."""
import argparse
import os

from .initializer import get_orekit_vm, init_orekit
from .utils import ValidUrlOrFile

ENABLED = bool(os.getenv("PYREBAR_HOOKS_ENABLED", "True"))


def pre_init(parser: argparse.ArgumentParser):
    """py-rebar pre-init hook.

    Args:
        parser (argparse.ArgumentParser): Argument parser used to parse the
        command line.
    """
    global ENABLED
    if not ENABLED:
        return

    if parser:
        parser.add_argument(
            "--orekit-data",
            help="Path to the data configuration. Can be a url or path to data on the local filesystem.",  # noqa: E501
            type=str,
            action=ValidUrlOrFile,
            dest="orekit_data",
            default="https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip",  # noqa: E501
        )


def post_init(args: argparse.Namespace = None):
    """pyrebar post-init hook.

    Args:
        args (argparse.Namespace): Command line arguments.

    Raises:
        RuntimeError: when the orekit vm initialization fails
    """
    global ENABLED
    if not ENABLED:
        return

    vm = get_orekit_vm()
    if not vm:
        raise RuntimeError("Failed to initialize the orekit vm.")

    if args and "orekit_data" in args and args.orekit_data:
        init_orekit(source=args.orekit_data)
