"""
Download (if necessary) the data file and provide a handle to it.
"""

import logging
import os
import os.path
import requests
import shutil
import tempfile


class Dataloader:
    """Utility to download files into a temporary data directory."""

    data_dir = os.path.join(tempfile.gettempdir(), "orekit_data")
    """Data directory where downloaded files will be stored."""

    @staticmethod
    def download(
        url: str,
        reload: bool = False,
        headers: dict = {
            "accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",  # noqa: E501
        },
    ) -> str:
        """
        Download a file to the temporary data data directory

        Args:
            url (str): url to download
            reload (bool, optional): Indicate whether to always reload the file, even if
            it is present in the data directory. Defaults to False.
            headers (dict, optional): HTTP headers to include in the request. Defaults
            to accept all types and provide a default `User-Agent` definition.

        Returns:
            str: The path to the downloaded file on the file system.
        """
        name = os.path.basename(url)
        dest = os.path.join(Dataloader.data_dir, name)

        if os.path.exists(dest) and not reload:
            return dest

        if not os.path.exists(Dataloader.data_dir):
            os.makedirs(Dataloader.data_dir)

        logging.getLogger(__name__).debug("HTTP GET %s", url)
        r = requests.get(
            url,
            stream=True,
            headers=headers,
        )
        logging.getLogger(__name__).debug("HTTP GET response: %d", r.status_code)

        with open(dest, "wb") as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        return dest

    @staticmethod
    def clearCache(ignore_errors: bool = False, onerror=None):
        """
        Clear any and all cached data.

        Args:
            ignore_error (bool, optional): Passed directly to shutil.rmtree. Defaults
            to False
            onerror (_OnErrorCallback | None, optional): Passed directly to
            shutil.rmtree. Defaults to None
        """
        shutil.rmtree(
            path=Dataloader.data_dir, ignore_errors=ignore_errors, onerror=onerror
        )
