
from datetime import datetime
import logging
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

from ..base import SchemaBase
from ...constants import ELEM
from .file_metadata import FileMetadata
from ...utils import datetime_from_str

log = logging.getLogger(__name__)

class Schema1(SchemaBase):
    schema_version = "1"

    _action = "action"
    _install = "install"
    _version = "version"

    def __init__(self, root):
        """Initialize Schema1 with the root element of the swinstall_stack xml tree.

        :param root: root element of document.
        :type root: ElementTree.Element"""
        super(Schema1, self).__init__(root)
