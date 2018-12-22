"""
utils.py

Utility functions for project.
"""

from datetime import datetime
import logging
from .constants import DATETIME_FORMAT

__all__ = ("datetime_from_str", "datetime_revision_from_str", "datetime_to_str")

LOG = logging.getLogger(__name__)

def datetime_from_str(datetime_str):
    """Given a string of the form YYYMMDD-HHMMSS, return a datetime instance.

    :param datetime_str: (str) representing a specific date and time
    :returns: datetime instance"""
    return datetime.strptime(datetime_str, DATETIME_FORMAT)


def datetime_revision_from_str(datetime_str):
    """Given a string of the form YYYMMDD-HHMMSS, return a datetime instance.

    :param datetime_str: string representing a specific date and time
    :type datetime_str: str

    :returns: datetime instance and revision
    :rtype: tuple(datetime, str | None)
    """
    revision = None
    if "_" in datetime_str:
        pieces = datetime_str.split("_")
        revision = pieces.pop()
        datetime_str = pieces.pop()
    rval = (datetime.strptime(datetime_str, DATETIME_FORMAT), revision)
    return rval

def datetime_to_str(date_time):
    """Given a datetime instance, return a string formatted appropriately.

    :param date_time: the datetime instance
    :type date_time: datetime

    :returns: datetime string matching constants.DATETIME_FORMAT
    :rtype: str
    """
    assert isinstance(date_time, datetime), \
        "datetime_to_str accepts a datetime instance. not {}"\
        .format(date_time.__class__.__name__)

    return date_time.strftime(DATETIME_FORMAT)

