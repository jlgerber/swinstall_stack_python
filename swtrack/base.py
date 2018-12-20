import os
import xml.etree.ElementTree as ET

class SchemaBase(object):
    schema_version = None
    registry = {}

    @classmethod
    def register(cls, schema):
        """Register a schema class with the registry, which is used
        to instantiate the appropriate schema version, supporting multiple
        schema generations.
        """
        cls.registry[schema.schema_version] = schema

    @classmethod
    def parse(cls, swinstall_stack):
        tree = ET.parse(swinstall_stack)
        root = tree.getroot()
        schema_version = root.attrib.get("schema")

        if schema_version:
            if not cls.registry.has_key(schema_version):
                raise KeyError("Schema registry missing schema version: {}. Registered versions:{}"\
                .format(schema_version, cls.registry.keys()))
            return cls.registry.get(schema_version)(root)

        raise ValueError("Root xml element does not have schema attribute")

    def __init__(self, root):
        """Initialize the BaseSchema class, validating the schema_version registered
        on the parent class against the schema version declared in the root xml element.

        :param root: Root xml Element of class ElementTree.Node
        :type root: ElementTree.Element
        """
        self._validate_schema_version(root)
        self._root = root
        self._swinstall_stack = root.attrib.get("path")

    def root_dirname(self):
        """Return the directory name of the root path.

        :return: Directory name of root.path
        :rtype: str
        """
        return os.path.dirname(self.root.attrib.get("path"))

    def _validate_schema_version(self, root):
        """Validate the schema version of the calling class against the schema version
        declared in the root element

        :param root: root xml element
        :type root: ElementTree.Node
        :returns: None
        :raises: ValueError
        """
        root_schema_version = root.attrib.get("schema")
        if self.__class__.schema_version != root_schema_version:
            raise ValueError("wrong schema version {} for class: {} schema:{}"\
            .format(root_schema_version, self.__class__.__name__, self.__class__.schema_version))

    @property
    def swinstall_stack(self):
        """The full path to the swinstall_stack file.

        :return: full path to swinstall_stack file
        :rtype: str
        """
        return self._swinstall_stack

    @property
    def root(self):
        """The root Element of the swinstall_stack document.

        :return: root element of swinstall_stack document
        :rtype: ElementTree.Element
        """
        return self._root

    def current(self):
        """Return metadata corresponding with the current file in the swinstall stack.
        """
        raise NotImplementedError()

    def next_version(self):
        """Return the next available version number after the current one.

        :return: next version number after the current one.
        :rtype: int
        """
        raise NotImplementedError()

    def current_version(self):
        """Return the current version number.

        :return: Current version number
        :rtype: int
        """
        raise NotImplementedError()

    def version(self, version):
        """retrieve metadata for the swinstalled file entry with the supplied
        version number.

        :param version: version of interest
        :type version: int
        """
        raise NotImplementedError()

    def file_on(self, date_time):
        """Retrieve the versioned file corresponding to the specified date.

        :param date_time: What date and time we want to look up the file at.
                        `file_on` will return the latest file in the swinstall_stack
                        whose datetime is less than or equal to the supplied *date_time*
                        parameter.
        :type date_time: datetime instance
        :return: filepath to versioned file
        :rtype: str
        :raises: KeyError - If date_time is invalid
        """
        raise NotImplementedError()

    def insert_element(self, hash, datetime, revision=None):
        """Insert a new element with the supplied properties.

        :param hash: hash of the file contents that the element wraps
        :param datetime: (datetime) that the new element was created
        :param revision: (str) optional revision id from VCS.
        """
        raise NotImplementedError()

    def rollback_element(self, date_time):
        """Rollback the current entry to point at the previous entry.

        :param date_time: The datetime at which the rollback occured
        :type date_type: datetime instance
        """
        raise NotImplementedError()