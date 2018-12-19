

from datetime import datetime
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

from .base import SchemaBase
from .constants import ELEM
from .swinstallfile import SwinstallFile
from .utils import datetime_from_str

class Schema2(SchemaBase):
    schema_version = "2"

    _action = "action"
    _install = "install"
    _version = "version"

    def __init__(self, root):
        """Initialize Schema2 with the root element of the swinstall_stack xml tree.

        :param root: ElementTree.Element"""
        super(Schema2, self).__init__(root)

    def current(self):
        """Return the current swinstallfile metadata.

        :returns SwinstallFile: metadata describing current swinstalled file
        """
        return SwinstallFile(self.root, **self.root.iter(ELEM).next().attrib)

    def next_version(self):
        """Returns the next version number after the current one.

        :returns int:
        """
        for child in self.root:
            if child.attrib.get(self._action) == self._install:
                return int(child.attrib.get(self._version)) + 1

    def current_version(self):
        """Returns the current version number.

        :returns int: The current version number"""
        return int(self.root.iter(ELEM).next().attrib.get(self._version))

    def version(self, version):
        """retrieve the version passed in

        :param int version: The version number corresponding
                            to the swinstall file metadata
                            we whish to look up.
        :returns SwinstallFile: Instance of file metadata
        :raises KeyError: if the version passed in does not exist
        """
        for child in self.root:
            if child.attrib.get(self._version) == str(version):
                return SwinstallFile(self.root, **child.attrib)
        raise KeyError("no version: {} has been published",format(version))

    def insert_element(self, hash, date_time=datetime.now(),  revision=None):
        """Generate a new element from a given date_time object.

        :param hash: (str) Hash of file contents.
        :param date_time: (datetime) optional instance of datetime class.
                          Will generate datetime for current date and time
                          if none is supplied
        :param revision: None|str - The optional scm revision number
        """
        next_version = self.next_version()
        #self, root, action, version, datetime, hash, revision=None):
        next = SwinstallFile(self.root, "install", next_version, date_time, hash, revision)
        self._insert_element(next.element())

    def rollback_element(self, date_time=datetime.now()):
        """A rollback sets the new current version to old current version - 1

        :param date_time: (datetime) of the rollback operation. It defaults to datetime.now()
        :returns None:"""
        new_version = self.current_version() - 1
        installfile = self.version(new_version)
        rollback = SwinstallFile(self.root, "rollback", new_version, date_time, installfile.hash, installfile.revision)
        self._insert_element(rollback.element())

    def _insert_element(self, element):
        self.root.insert(0, element)
        xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ", encoding='UTF-8')
        xmlstr = os.linesep.join([s for s in xmlstr.splitlines() if s.strip()])
        output = self.root.attrib.get("path")
        print "outputing to {}".format(output)
        with open(output, "w") as f:
            f.write(xmlstr)

    def file_on(self, date_time):
        """Given a datetime instance, find the most recent action which is less than or
        equal to the datetime.

        :param date_time: (datetime) used to constrain the lookup of file metadata to.
                          We find the most recent change in the log whose datetime
                          attribute is less than or equal to the supplied date_time
        :returns SwinstallFile: file metadata if found
        :raises LookupError: If unable to find an entry which is less than or equal to the
                             supplied datetime instance"""
        dt = datetime_from_str(date_time)
        for child in self.root:
            if datetime_from_str(child.datetime) <= dt:
                return SwinstallFile(path=self.root, **child.attrib)
        basename = os.path.basename(os.path.dirname(self.root.attrib.get("path")))
        raise LookupError("unable to find version of {} installed on or before {}".format(basename, date_time))
