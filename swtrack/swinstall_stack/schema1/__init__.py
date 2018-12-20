
__all__ = ("Schema1",)

from datetime import datetime
import logging
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

from ..base import SchemaBase
from ...constants import (ELEM, DEFAULT_SCHEMA)
from .file_metadata import FileMetadata
from ...utils import (datetime_from_str, datetime_revision_from_str, datetime_to_str)

log = logging.getLogger(__name__)

class Schema1(SchemaBase):
    schema_version = DEFAULT_SCHEMA

    _action = "action"
    _install = "install"
    _version = "version"

    def __init__(self, root):
        """Initialize Schema1 with the root element of the swinstall_stack xml tree.

        :param root: root element of document.
        :type root: ElementTree.Element"""
        super(Schema1, self).__init__(root)

    def current(self):
        """Return metadata corresponding with the current file in the swinstall stack.
        """
        for elt in self.root:
            if elt.attrib.get("is_current") == "True":
                return FileMetadata.init_from_version_str(self.root_dirname(), **elt.attrib)

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
                return datetime_from_str(elt.attrib.get("version"))
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
        version = datetime_from_str(version) if isinstance(version, basestring) else version
        for elt in self.root:
            if datetime_revision_from_str(elt.attrib.get("version"))[0] == version:
                return FileMetadata.init_from_version_str(self.root_dirname(), **elt.attrib)
        raise KeyError("no version: {} has been published",format(version))

    def file_on(self, date_time):
        """Retrieve the versioned file corresponding to the specified date.

        :param date_time: What date and time we want to look up the file at.
                        `file_on` will return the latest file in the swinstall_stack
                        whose datetime is less than or equal to the supplied *date_time*
                        parameter.
        :type date_time: datetime instance

        :returns: filepath to versioned file
        :rtype: str

        :raises: KeyError - If date_time is invalid
        """
        assert isinstance(date_time, datetime), "file_on takes an instance of datetime, not a {}".format(date_time.__class__.__name__)
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
                    raise ValueError("no version less than or equal to {}"\
                    .format(datetime_to_str(date_time)))
                return self._versioned_file(latest, latest_revision)
            if is_current:
                # if we are current, we may exit before the
                if not latest:
                    raise ValueError("current version not less than or equal to {}"\
                    .format(datetime_to_str(date_time)))
                return self._versioned_file(latest, latest_revision)

        raise ValueError("no version less than or equal to {}".format(datetime_to_str(date_time)))

    def _versioned_file(self, date_time, revision_str):
        revision = "" if revision_str is None else "_{}".format(revision_str)
        return os.path.join(self.root_dirname(),
                "{}_{}{}".format(self.versionless_filename(), date_time, revision))

    def insert_element(self, hash, datetime, revision=None):
        """Insert a new element with the supplied properties.

        :param hash: hash of the file contents that the element wraps
        :type hash: str
        :param datetime: that the new element was created
        :type datetime: datetime
        :param revision: optional revision id from VCS.
        :type revision: str
        """
        raise NotImplementedError()

    def rollback_element(self, date_time):
        """Rollback the current entry to point at the previous entry.

        :param date_time: The datetime at which the rollback occured
        :type date_type: datetime instance
        """
        raise NotImplementedError()


SchemaBase.register(Schema1)