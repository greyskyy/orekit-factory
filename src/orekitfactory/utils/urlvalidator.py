"""Validate URLs."""
import argparse
import os.path
import urllib.parse


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid url.

    Args:
        url (str): The string to check

    Returns:
        bool: `True` if the string is a valid url; `False` otherwise.
    """
    if url:
        tmp = urllib.parse.urlparse(url)
        return True if tmp.scheme and tmp.netloc else False
    return False


class ValidUrlOrFile(argparse.Action):
    """Argparse action to require valid files or url strings."""

    def __init__(*args, **kwargs):
        """Class constructor."""
        argparse.Action.__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, (list, tuple)):
            new_values = []
            for v in values:
                if is_valid_url(v) or os.path.exists(v):
                    new_values.append(v)
                else:
                    raise ValueError(f"Value is not a url or file path [value={v}]")
            setattr(namespace, self.dest, new_values)
        elif is_valid_url(values) or os.path.exists(values):
            setattr(namespace, self.dest, values)
        else:
            raise ValueError(f"Value is not a url or file path [value={v}]")
