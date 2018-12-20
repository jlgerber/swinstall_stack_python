
import os
import xml.etree.ElementTree as ET
from ...constants import (DATETIME_FORMAT, ELEM)

class FileMetadata(object):
    """Class which tracks metadata associated with an swinstalled file."""

    def __init__(self, path, action, version, datetime, hash, revision=None):
        """Initialize an instance of FileMetadata with metadata
        :param path: (ElementTree.Element) instance of root xml node
        :param action: (str) The action performed by the entry (install|rollback)
        :param version: (str) The version number of the entry in swinstall stack
        :param datetime: (datetime) the time at which the tracked action occured.
        :param hash: (str) a hex sequence stored as a string which represents a hash
                     of the contents of the file that the entry tracks
        :param revision: (str) an optional revision id of the tracked file in SCM
        """
        self._path = path#os.path.dirname(root.attrib.get("path"))
        self._action = action
        self._version = int(version)
        self._datetime = datetime
        self._hash = hash
        self._revision = revision

    def __str__(self):
        return "FileMetadata <action:{} version:{} datetime:{} hash:{} revision:{}>"\
        .format(self.action, self.version, self.datetime, self.hash, self.revision)

    def element(self):
        """Return an XML element whose attributes correspond with those of the swinstall file.

        :returns: ElementTree.Element"""
        attrib_dict = {
            "action":self.action,
            "version": str(self.version),
            "datetime": self.datetime.strftime(DATETIME_FORMAT),
            "hash": self.hash
        }

        if self.revision:
            attrib_dict["revision"] = self.revision

        return ET.Element(ELEM, attrib=attrib_dict)

    @property
    def versionless_path(self):
        return self._path

    @property
    def action(self):
        return self._action

    @property
    def version(self):
        return self._version

    @property
    def datetime(self):
        return self._datetime

    @property
    def hash(self):
        return self._hash

    @property
    def revision(self):
        return self._revision

    def fullpath(self):
        """Return the full path to the specific file that the entry is tracking.

        :returns: (str) path to the tracked file
        """
        dirname = self.versionless_path
        basename = os.path.basename(dirname)
        return os.path.join(dirname,"{}_{}".format(basename, self.datetime))

    def __eq__(self, other):
        if self.versionless_path == other.versionless_path and \
        self.version == other.version and \
        self.datetime == other.datetime and \
        self.hash == other.hash and \
        self.revision == other.revision :
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
