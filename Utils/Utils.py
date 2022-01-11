from urllib.parse import urljoin
from urllib.request import pathname2url
from pathlib import Path


def file_path_to_url(path:Path) -> str:
    """
    converts an absolute native path to a FILE URL.

    Parameters
    ----------
    path : a path in native format

    Returns
    -------
    a valid FILE URL
    """
    return urljoin('file:', pathname2url(str(path.absolute())))