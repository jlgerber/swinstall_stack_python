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


STACK='''<stack_history path="/dd/facility/ext/bak/packages.xml/packages.xml_swinstall_stack">
    <elt is_current="False" version="20161213-093146_r575055" />
    <elt is_current="False" version="20181102-144204" />
    <elt is_current="True" version="20181105-103813" />
    <elt is_current="False" version="20181110-104603" />
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

    def test_parse(self):
        # we assert that this will not raise an exception
        Schema1.parse(self.versionless_file)

    def test_current(self):
        current = self.schema.current()
        expected = FileMetadata.init_from_version_str( self.schema.root_dirname(),
                                 "True",
                                 "20181105-103813")
        self.assertEqual(current, expected)

    def test_current_false(self):
        current = self.schema.current()
        expected = FileMetadata.init_from_version_str(self.schema.root_dirname(),
                                 "True",
                                 "20180702-144204")
        self.assertNotEqual(current, expected)


    def test_current_version(self):
        answer = self.schema.current_version()
        expected = datetime_from_str("20181105-103813")
        self.assertEqual(answer, expected)

    def test_version(self):
        answer = self.schema.version(datetime_from_str("20181102-144204"))
        expected = FileMetadata.init_from_version_str(self.schema.root_dirname(),
                                "False",
                                 "20181102-144204")

        self.assertEqual(answer,expected)

    def test_version_nomatch(self):
        with self.assertRaises(KeyError):
            self.schema.version("20171103-144204")

    def test_file_on_before_current(self):
        dt_str = "20181102-144204"
        dt = datetime_from_str(dt_str)
        result = self.schema.file_on(dt)
        expected = "/dd/facility/ext/bak/packages.xml/packages.xml_{}".format(dt_str)
        self.assertEqual(result, expected)

    def test_file_on_after_current(self):
        dt_str = "20181221-220000"
        dt = datetime_from_str(dt_str)
        result = self.schema.file_on(dt)
        expected = "/dd/facility/ext/bak/packages.xml/packages.xml_20181105-103813"
        self.assertEqual(result, expected)
