
__all__ = ("FileMetadata",)

import os
import xml.etree.ElementTree as ET
from ...constants import (DATETIME_FORMAT, ELEM)
from ...utils import datetime_from_str, datetime_to_str
from datetime import datetime

class FileMetadata(object):
    def __init__(self, path, is_current, version, revision=None):
        self._path = path
        self._is_current = is_current
        self._version = version
        self._revision = revision
        assert isinstance(version, datetime), "version must be of type datetime, not {}"\
                                                .format(version.__class__.__name__)
        # get a tuple containing the datetime and optionally the revision
        #datetime_revision = self._extract_datetime_and_revision(version)
        #self._version = datetime_revision[0]
        #if datetime_revision[1] and revision and (datetime_revision[1] != revision):
        #    raise ValueError("revision passed in explicitly does not match revision on datetime string")
        #self._revision = datetime_revision[1] or revision

    @classmethod
    def init_from_version_str(cls, path, is_current, version):
        """alternative constructor which takes a version string and initializes FileMetadata
        with it

        :param path: THe path to the versioned file
        :type path: str
        :param is_current: Whether the version is current or not
        :type is_current: stringified bool
        :param version: Version string which may be of the form YYYYMMDD-HHMMSS
                        or YYYYMMDD-HHMMSS_<revision>
        :type version: str

        :returns: FileMetadata instance
        """
        datetime_revision = cls._extract_datetime_and_revision(version)
        return cls(path, is_current, datetime_revision[0], datetime_revision[1])

    def __str__(self):
        return "FileMetadata <is_current:{} version:{} >"\
        .format(self.is_current,  self.version)


    def __repr__(self):
        return "FileMetadata <path: {} is_current:{} version:{} >"\
        .format(self.path,  self.is_current,  self.version)

    @staticmethod
    def _extract_datetime_and_revision(date_time):
        """Handles extracting revision from date_time if exant.
        Also handles converting from string to datetime.

        :param date_time: datetime instance or string, which may also contain
                          a revision id on the end from a VCS system
        :type date_time: datetime instance or str

        :returns: tuple of datetime and revision (or None)
        :rtype: (datetime, str|None)
        """
        if isinstance(date_time, datetime):
            return (date_time, None)
        if isinstance(date_time, basestring):
            if "_" in date_time:
                # peel revision off of date_time string and return tuple
                pieces = date_time.split("_")
                revision = pieces.pop()
                date_time = datetime_from_str(pieces.pop())
                return (date_time, revision)
            return (datetime_from_str(date_time), None)
        raise TypeError("Wrong type for date_time: {}. should be string or datetime".format(date_time.__class__.__name__))

    @property
    def versionless_path(self):
        versionless_path_dir = self.path.split("bak")[0]
        # _20181111-112233 = 16 chars
        # _11414214-425411_<revision> = 17 + revision length
        endlen = 16 if self.revision is None else 17 + len(self.revision)
        name = os.path.basename(self.path)[:-endlen]
        return os.path.join(versionless_path_dir, name)

    def element(self):
        """Return an XML element whose attributes correspond with those of the swinstall file.

        :returns: Xml Element initialized with file metadata.
        :rtype:  ElementTree.Element
        """
        def to_version():
            version = datetime_to_str(self.version)
            if self.revision != None:
                version = "{}_{}".format(version, self.revision)
            return version

        version = to_version()
        attrib_dict = {
            "is_current":self.is_current,
            "version": to_version()
        }

        return ET.Element(ELEM, attrib=attrib_dict)

    @property
    def is_current(self):
        return self._is_current

    @property
    def version(self):
        return self._version

    @property
    def revision(self):
        return self._revision
    @property
    def path(self):
        return self._path

    def fullpath(self):
       return self._path

    def __eq__(self, other):
        if self.path == other.path and \
        self.version == other.version and \
        self.revision == other.revision and \
        self.is_current == other.is_current :
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)