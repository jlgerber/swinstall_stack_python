
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
        """

        self._validate_schema_version(root)
        self._root = root
        self._swinstall_stack = root.attrib.get("path")

    def _validate_schema_version(self, root):
        """Validate the schema version of the calling class against the schema version
        declared in the root element

        :param root: ElementTree.Node root xml element
        :returns: None
        :raises: ValueError
        """
        root_schema_version = root.attrib.get("schema")
        if self.__class__.schema_version != root_schema_version:
            raise ValueError("wrong schema version {} for class: {} schema:{}"\
            .format(root_schema_version, self.__class__.__name__, self.__class__.schema_version))

    @property
    def swinstall_stack(self):
        return self._swinstall_stack

    @property
    def root(self):
        return self._root

    def current(self):
        """return metadata corresponding with the current file in the swinstall stack
        """
        raise NotImplementedError()

    def next_version(self):
        """Return the next available version number after the current one"""
        raise NotImplementedError()

    def current_version(self):
        """Return the current version number"""
        raise NotImplementedError()

    def version(self, version):
        """retrieve metadata for the swinstalled file entry with the supplied
        version number."""
        raise NotImplementedError()

    def file_on(self, filepath, date_time ):
        raise NotImplementedError()

    def insert_element(self, hash, datetime, revision):
        """insert a new element with the supplied properties"""
        raise NotImplementedError()

    def rollback_element(self, date_time):
        """Rollback the current entry to point at the previous entry.
        :param date_time: The datetime at which the rollback occured
        """
        raise NotImplementedError()