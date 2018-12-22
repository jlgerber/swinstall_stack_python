
"""
schema2.file_metadata.py

provide metadata about a version of an swisntall within
the swinstall_stack
"""

from datetime import datetime
import os
import xml.etree.ElementTree as ET
from ...constants import (DATETIME_FORMAT, ELEM)
from ...utils import datetime_from_str
from ..base.file_metadata import FileMetadataBase
from ..schema2 import Schema2

__all__ = ("FileMetadata",)

class FileMetadata(FileMetadataBase):
    """Class which tracks metadata associated with an swinstalled file."""

    def __init__(self, path, action, version, datetime_val, hash_str, revision=None):
        """Initialize an instance of FileMetadata with metadata.

        :param path: path to versioned file
        :type path: str
        :param action:  The action performed by the entry (install|rollback)
        :type action: str
        :param version: The version number of the entry in swinstall stack
        :type version: str
        :param datetime_val: the time at which the tracked action occured.
        :type datetime_val: datetime
        :param hash_str: A hex sequence stored as a string which represents a hash
                     of the contents of the file that the entry tracks
        :type hash_str: str
        :param revision: an optional revision id of the tracked file in SCM
        :type revision: str
        """
        self._path = path
        self._action = action
        self._version = int(version)
        self._datetime = self._set_datetime(datetime_val)
        self._hash = hash_str
        self._revision = revision

        super(FileMetadata, self).__init__()

    def __str__(self):
        return "FileMetadata <path:{} action:{} version:{} datetime:{} hash:{} revision:{}>"\
        .format(self.path,
                self.action,
                self.version,
                self.datetime,
                self.hash,
                self.revision)

    @staticmethod
    def _set_datetime(date_time):
        if isinstance(date_time, datetime):
            return date_time
        if isinstance(date_time, basestring):
            return datetime_from_str(date_time)
        raise TypeError("Wrong type for date_time: {}. should be string or datetime"\
                        .format(date_time.__class__.__name__))

    def element(self):
        """Return an XML element whose attributes correspond with
        those of the swinstall file.

        :returns: Xml Element initialized with file metadata.
        :rtype:  ElementTree.Element
        """
        attrib_dict = {
            "action":self.action,
            "version": str(self.version),
            "datetime": self.datetime.strftime(DATETIME_FORMAT),
            "hash": self.hash
        }

        if self.revision:
            attrib_dict["revision"] = self.revision

        return ET.Element(ELEM, attrib=attrib_dict)

    def is_current(self):
        """Test to see if the metadata points at a current
        entry in the swinstall_log
        """
        # get the path to the versionless file
        base_path = self.path.split("bak")[0]
        base_path = os.path.join(base_path, self.versionless_path)
        schema = Schema2.parse(base_path)
        current = schema.current()
        return self == current

    @property
    def path(self):
        """read only property"""
        return self._path

    @property
    def versionless_path(self):
        """read only property"""
        return os.path.basename(
            os.path.dirname(
                self.path
            )
        )

    @property
    def action(self):
        """read only property"""
        return self._action

    @property
    def version(self):
        """read only property"""
        return self._version

    @property
    def datetime(self):
        """read only property"""
        return self._datetime

    @property
    def hash(self):
        """read only property"""
        return self._hash

    @property
    def revision(self):
        """read only property"""
        return self._revision

    def __eq__(self, other):
        assert isinstance(other, FileMetadata), \
               "cannot compare FileMetadata to {}".format(other.__class__.__name__)
        if self.path == other.path and \
        self.version == other.version and \
        self.datetime == other.datetime and \
        self.hash == other.hash and \
        self.revision == other.revision:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

