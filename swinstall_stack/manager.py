"""
manager.py

entrypoint for swinstall stack parsing
"""

#from datetime import datetime
import time
import logging
import os
import xml.etree.ElementTree as ET
from .constants import DEFAULT_SCHEMA

LOG = logging.getLogger(__name__)

__all__ = ("SwinstallStackMgr",)


class SwinstallStackMgr(object):
    """Manager class responsible for identifying schema version of
    swinstall_stack and delegating parsing duities to apporpriate
    schema class.
    The manager maintains a registry of schema classes which it
    uses at runtime to draw upon.
    """
    registry = {}

    @classmethod
    def register(cls, schema):
        """Register a schema class with the registry, which is used
        to instantiate the appropriate schema version, supporting multiple
        schema generations.

        :param schema: class to register. This classmethod uses the subclass's
                       schma_version class variable as the key in the registry.
        :type schema: SchemaCommon subclass
        """
        cls.registry[schema.schema_version] = schema

    def __init__(self):
        """Initialize the parent class"""
        super(SwinstallStackMgr, self).__init__()

    @staticmethod
    def _swinstall_stack_from_file(swinstalled_file):
        """given the fullpath to an swinstalled file, construct the
        full path to the relevant schemas

        :param swinstalled_file: Full path to the swinstalled file
        :type swinstalled_file: str

        :returns: full path to schemas
        :rtype: str
        """
        file_name = os.path.basename(swinstalled_file)
        dir_name = os.path.dirname(swinstalled_file)
        return os.path.join(dir_name, "bak", file_name, \
                "{}_swinstall_stack".format(file_name))

    def parse(self, swinstalled_file):
        """Given the full path to a versionless swinstalled file, locate the swinstall
        stack and parse the stack to determine the schema version. then,
        invoke the approprate subclass parsing method, returning an initialized
        subclass of SchemaCommon.

        :param swinstalled_file: fullpath to swinstalled file
        :type swinstalled_file: str

        :returns: SchemaCommon subclass instance
        :rtype: SchemaCommon subclass

        :raises: ValueError if unable to identify schema version
        """
        cls = self.__class__
        start_time = int(time.time())

        tree = ET.parse(self._swinstall_stack_from_file(swinstalled_file))
        root = tree.getroot()
        schema_version = root.attrib.get("schema", DEFAULT_SCHEMA)
        
        if schema_version:
            if not cls.registry.has_key(schema_version):
                raise KeyError("Schema registry missing schema version: {}. Registered versions:{}"\
                .format(schema_version, cls.registry.keys()))
            return cls.registry.get(schema_version)(root, start_time)

        raise ValueError("Root xml element does not have schema attribute")
