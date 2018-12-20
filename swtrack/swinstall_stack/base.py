__all__ = ("SchemaBase", "SchemaInterface")

import os
import xml.etree.ElementTree as ET
from  ..constants import DEFAULT_SCHEMA

class SchemaBase(object):
    """Base class providing schema registry, as well as callable methods.
    """
    schema_version = None
    registry = {}

    @classmethod
    def register(cls, schema):
        """Register a schema class with the registry, which is used
        to instantiate the appropriate schema version, supporting multiple
        schema generations.

        :param schema: class to register. This classmethod uses the subclass's
                       schma_version class variable as the key in the registry.
        :type schema: SchemaBase subclass
        """
        cls.registry[schema.schema_version] = schema

    @staticmethod
    def _swinstall_stack_from_file(swinstalled_file):
        """given the fullpath to an swinstalled file, construct the
        full path to the relevant swinstall_stack

        :param swinstalled_file: Full path to the swinstalled file
        :type swinstalled_file: str

        :returns: full path to swinstall_stack
        :rtype: str
        """
        file_name = os.path.basename(swinstalled_file)
        dir_name = os.path.dirname(swinstalled_file)
        return os.path.join(dir_name, "bak", file_name, \
                "{}_swinstall_stack".format(file_name))

    @classmethod
    def parse(cls, swinstalled_file):
        """Given the full path to a versionless swinstalled file, locate the swinstall
        stack and parse the stack to determine the schema version. then,
        invoke the approprate subclass parsing method, returning an initialized
        subclass of SchemaBase.

        :param swinstalled_file: fullpath to swinstalled file
        :type swinstalled_file: str

        :returns: SchemaBase subclass instance
        :rtype: SchemaBase subclass

        :raises: ValueError if unable to identify schema version
        """
        tree = ET.parse(cls._swinstall_stack_from_file(swinstalled_file))
        root = tree.getroot()
        schema_version = root.attrib.get("schema", DEFAULT_SCHEMA)

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
        fullpath = self.root.attrib.get("path")
        #assert fullpath != None, "root attrib path is None"
        dirname =  os.path.dirname(fullpath)
        #assert dirname != None, "root dirname is None"
        return dirname

    def versionless_filename(self):
        """Return the versionless name of the swinstalled file

        :returns: Versionless swinstalled file name
        :rtype: str
        """
        return os.path.basename(self.root_dirname())

    def _validate_schema_version(self, root):
        """Validate the schema version of the calling class against the schema version
        declared in the root element

        :param root: root xml element
        :type root: ElementTree.Node

        :returns: None

        :raises: ValueError
        """
        root_schema_version = root.attrib.get("schema", DEFAULT_SCHEMA)
        if self.__class__.schema_version != root_schema_version:
            raise ValueError("wrong schema version {} for class: {} schema:{}"\
            .format(root_schema_version, self.__class__.__name__, self.__class__.schema_version))

    @property
    def swinstall_stack(self):
        """The full path to the swinstall_stack file.

        :returns: full path to swinstall_stack file
        :rtype: str
        """
        return self._swinstall_stack

    @property
    def root(self):
        """The root Element of the swinstall_stack document.

        :returns: root element of swinstall_stack document
        :rtype: ElementTree.Element
        """
        return self._root


class SchemaInterface(object):
    """abstract class providing minimum set of methods defining the schema interface"""
    def current(self):
        """Return metadata corresponding with the current file in the swinstall stack.
        """
        raise NotImplementedError()

    def current_version(self):
        """Return the current version .

        :returns: Current version
        :rtype: cls._version_type
        """
        raise NotImplementedError()

    def version(self, version):
        """retrieve metadata for the swinstalled file entry with the supplied
        version.

        :param version: version of interest
        :type version: cls._version_type
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def insert_element(self, *args, **kwargs):
        """Insert a new element with the supplied properties
        """
        raise NotImplementedError()

    def rollback_element(self, date_time):
        """Rollback the current entry to point at the previous entry.

        :param date_time: The datetime at which the rollback occured
        :type date_type: datetime instance
        """
        raise NotImplementedError()


