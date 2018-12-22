
__all__ = ("Schema1",)

from datetime import datetime
import logging
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

from ..base import SchemaCommon, SchemaBase
from ...constants import (ELEM, DEFAULT_SCHEMA)
from .file_metadata import FileMetadata
from ...utils import (datetime_from_str, datetime_revision_from_str, datetime_to_str)

log = logging.getLogger(__name__)

class Schema1(SchemaCommon, SchemaBase):
    schema_version = DEFAULT_SCHEMA

    _action = "action"
    _install = "install"
    _version = "version"

    def __init__(self, root):
        """Initialize Schema1 with the root element of the schemas xml tree.

        :param root: root element of document.
        :type root: ElementTree.Element"""
        super(Schema1, self).__init__(root)

    def current(self):
        """Return metadata corresponding with the current file in the swinstall stack.
        """
        for elt in self.root:
            if elt.attrib.get("is_current") == "True":
                date_time, revision = datetime_revision_from_str(elt.attrib.get("version"))
                versioned_filepath = self._versioned_file( date_time, revision)
                return FileMetadata.init_from_version_str(versioned_filepath, **elt.attrib)

        raise ValueError("Unable to find current")

    def next_version(self):
        """Not implmemented for Schema 1.

        :raises: NotImplementedError
        """
        raise NotImplementedError()

    def current_version(self):
        """Return the current version number.

        :returns: Current version
        :rtype: datetime
        """
        for elt in self.root:
            if elt.attrib.get("is_current") == "True":
                return datetime_revision_from_str(elt.attrib.get("version"))[0]
        raise ValueError("No current version")

    def version(self, version):
        """retrieve metadata for the swinstalled file entry with the supplied
        version number.

        :param version: version of interest
        :type version: datetime or str

        :returns: metadata of the matching file
        :rtype: schema1.FileMetadata

        :raises: KeyError if version does not match any versions
        """
        # convert to a datetime if we are a string
        version = datetime_from_str(version) if isinstance(version, basestring) else version
        for elt in self.root:
            # retrieve the datetime and revision from version
            date_time, revision = datetime_revision_from_str(elt.attrib.get("version"))
            if date_time == version:
                versioned_filepath = self._versioned_file(date_time, revision)
                return FileMetadata.init_from_version_str(versioned_filepath, **elt.attrib)
        raise KeyError("no version: {} has been published",format(version))

    def file_on(self, date_time):
        """Retrieve the versioned file corresponding to the specified date.

        :param date_time: What date and time we want to look up the file at.
                        `file_on` will return the latest file in the schemas
                        whose datetime is less than or equal to the supplied *date_time*
                        parameter.
        :type date_time: datetime instance

        :returns: filepath to versioned file
        :rtype: str

        :raises: LookupError - If date_time is invalid
        """
        date_time = datetime_from_str(date_time) if isinstance(date_time, basestring) else date_time
        latest = None
        latest_revision = None
        is_current = False
        current = None
        current_revision = None
        for elt in self.root:
            if elt.attrib.get("is_current") == "True":
                is_current = True
            current, current_revision = datetime_revision_from_str(elt.attrib.get("version"))

            if current <= date_time:
                latest = datetime_to_str(current)
                latest_revision = current_revision
            else:
                if not latest:
                    raise LookupError("no version less than or equal to {}"\
                    .format(datetime_to_str(date_time)))
                return FileMetadata( \
                    self._versioned_file(latest, latest_revision), \
                    "False", datetime_from_str(latest), latest_revision)
            if is_current:
                # if we are current, we may exit before the
                if not latest:
                    raise LookupError("current version not less than or equal to {}"\
                    .format(datetime_to_str(date_time)))
                return FileMetadata( \
                    self._versioned_file(latest, latest_revision),
                    "True", datetime_from_str(latest), latest_revision)

        raise LookupError("no version less than or equal to {}".format(datetime_to_str(date_time)))

    def _versioned_file(self, date_time, revision_str):
        """Given a date_time (datetime | str) and an optional revision_str, return
        the full path to the versioned file"""
        revision = "" if revision_str is None else "_{}".format(revision_str)
        date_time = datetime_to_str(date_time) if isinstance(date_time, datetime) else date_time
        return os.path.join(self.root_dirname(),
                "{}_{}{}".format(self.versionless_filename(), date_time, revision))

    def _insert_element_into_root(self, element):
        for child in self.root:
            if child.attrib.get("is_current") == "True":
                child.attrib['is_current'] = "False"
        self.root.append(element)
        log.debug("Added child: {} to root: {}".format(element.attrib, self.root.attrib))
        self._save()

    def insert_element(self, date_time, revision=None):
        """Insert a new element with the supplied properties.

        :param date_time: that the new element was created
        :type date_time: datetime
        :param revision: optional revision id from VCS.
        :type revision: str
        """
        log.debug("insert_element datetime:{} revision:{}".format(date_time, revision))
        next = FileMetadata(self._versioned_file(date_time, revision), "True", date_time, revision)
        self._insert_element_into_root(next.element())

    def rollback_element(self, date_time=datetime.now()):
        """Rollback the current entry to point at the previous entry.

        :param date_time: The datetime at which the rollback occured
        :type date_type: datetime instance
        """
        # iterate through elements, looking for current
        # set current to false
        # set current element index -1 to true
        # save
        cnt = 0
        for elt in self.root:
            if elt.attrib.get("is_current") == "True":
                elt.attrib["is_current"] = "False"
                lookup = cnt -1
                if lookup < 0:
                    raise IndexError("Attempt to roll back before start")
                list(self.root)[lookup].attrib["is_current"] = "True"
                break
            cnt +=1
        self._save()

SchemaCommon.register(Schema1)