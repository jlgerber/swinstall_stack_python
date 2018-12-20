
__all__ = ("Schema2",)

from datetime import datetime
import logging
import os

import xml.etree.ElementTree as ET

from ..base import SchemaBase, SchemaInterface
from ...constants import ELEM
from .file_metadata import FileMetadata
from ...utils import datetime_from_str

log = logging.getLogger(__name__)

class Schema2(SchemaBase, SchemaInterface):
    schema_version = "2"

    _action = "action"
    _install = "install"
    _version = "version"

    def __init__(self, root):
        """Initialize Schema2 with the root element of the swinstall_stack xml tree.

        :param root: root element of document.
        :type root: ElementTree.Element"""
        super(Schema2, self).__init__(root)

    def current(self):
        """Return the current file_metadata metadata.

        :returns:  metadata describing current swinstalled file
        :rtype: FileMetadata
        """
        return FileMetadata(self.root_dirname(), **self.root.iter(ELEM).next().attrib)

    def next_version(self):
        """Returns the next version number after the current one.

        :returns: Next version number
        :rtype: int
        """
        if len(self.root) == 0:
            log.debug("no children under root tag. returning 1 as next version")
            return 1
        for child in self.root:
            if child.attrib.get(self._action) == self._install:
                return int(child.attrib.get(self._version)) + 1

        raise RuntimeError("unable to find next version")

    def current_version(self):
        """Returns the current version number.

        :returns: The current version number
        :rtype: int"""
        return int(self.root.iter(ELEM).next().attrib.get(self._version))

    def version(self, version):
        """retrieve the version passed in

        :param int version: The version number corresponding
                            to the swinstall file metadata
                            we whish to look up.
        :returns: Instance of file metadata
        :rtype:  FileMetadata
        :raises KeyError: if the version passed in does not exist
        """
        for child in self.root:
            if child.attrib.get(self._version) == str(version):
                return FileMetadata(self.root_dirname(), **child.attrib)
        raise KeyError("no version: {} has been published",format(version))


    def _insert_element_into_root(self, element):
        self.root.insert(0, element)
        self._save()

    def insert_element(self, hash, date_time=datetime.now(),  revision=None):
        """Generate a new element from a given date_time object.

        :param hash: (str) Hash of file contents.
        :type hash: str
        :param date_time: (datetime) optional instance of datetime class.
                          Will generate datetime for current date and time
                          if none is supplied
        :type date_time:
        :param revision: None|str - The optional scm revision number
        """
        next_version = self.next_version()
        next = FileMetadata(self.root, "install", next_version, date_time, hash, revision)
        self._insert_element_into_root(next.element())

    def rollback_element(self, date_time=datetime.now()):
        """A rollback sets the new current version to old current version - 1

        :param date_time: (datetime) of the rollback operation. It defaults to datetime.now()
        :returns None:"""
        new_version = self.current_version() - 1
        installfile = self.version(new_version)
        rollback = FileMetadata(os.path.dirname(self.root.attrib.get("path")), "rollback", new_version, date_time, installfile.hash, installfile.revision)
        self._insert_element_into_root(rollback.element())


    def file_on(self, date_time):
        """Given a datetime instance, find the most recent action which is less than or
        equal to the datetime.

        :param date_time: (datetime) used to constrain the lookup of file metadata to.
                          We find the most recent change in the log whose datetime
                          attribute is less than or equal to the supplied date_time
        :returns FileMetadata: file metadata if found
        :raises LookupError: If unable to find an entry which is less than or equal to the
                             supplied datetime instance"""
        dt = datetime_from_str(date_time)
        for child in self.root:
            if datetime_from_str(child.datetime) <= dt:
                return FileMetadata(path=self.root_dirname(), **child.attrib)
        basename = os.path.basename(os.path.dirname(self.root.attrib.get("path")))
        raise LookupError("unable to find version of {} installed on or before {}".format(basename, date_time))


SchemaBase.register(Schema2)