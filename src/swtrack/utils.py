from datetime import datetime
from .constants import DATETIME_FORMAT
__all__ = ("datetime_from_str",)

def datetime_from_str(datetime_str):
    """Given a string of the form YYYMMDD-HHMMSS, return a datetime instance.

    :param datetime_str: (str) representing a specific date and time
    :returns: datetime instance"""
    return datetime.strptime(datetime_str,DATETIME_FORMAT)
