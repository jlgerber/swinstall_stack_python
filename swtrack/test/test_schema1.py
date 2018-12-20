#initialize testing environment
import env
# imports
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from swtrack.swinstall_stack.schema1 import Schema1
from swtrack.swinstall_stack.schema1.file_metadata import FileMetadata
from swtrack.utils import datetime_from_str


STACK='''<stack_history path="/Users/jonathangerber/src/python/swinstall_proposal/examples/schema1/bak/packages.xml/packages.xml_swinstall_stack">
    <elt is_current="False" version="20161213-093146_r575055" />
    <elt is_current="False" version="20181102-144204" />
    <elt is_current="True" version="20181105-103813" />
    <elt is_current="False" version="20181106-104603" />
</stack_history>
'''


class Schema1Test(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.mkdtemp()
        self.versionless_file = os.path.join(tmpdir, "packages.xml")
        self.fullpath = os.path.join(tmpdir, "bak", "packages.xml")
        os.makedirs(self.fullpath)
        self.swinstall_stack = os.path.join(self.fullpath, "packages.xml_swinstall_stack")

        with open(self.swinstall_stack,'w') as fh:
            fh.write(STACK)

        tree = ET.parse(self.swinstall_stack)
        root = tree.getroot()
        self.schema = Schema1(root)

    def tearDown(self):
        os.remove(self.swinstall_stack)
        os.rmdir(self.fullpath)
        del self.schema
