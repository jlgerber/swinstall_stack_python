#initialize testing environment
import env
# imports
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from swinstall_stack.schemas.base import SchemaBase
from swinstall_stack.utils import datetime_from_str
from swinstall_stack.constants import DEFAULT_SCHEMA, ELEM
"""
"""

STACK='''<stack_history path="/dd/facility/etc/bak/packages.xml/packages.xml_swinstall_stack">
    <elt is_current="False" version="20161213-093146_r575055" />
    <elt is_current="False" version="20181102-144204" />
    <elt is_current="True" version="20181105-103813" />
    <elt is_current="False" version="20181110-104603" />
</stack_history>
'''

class SchemaBaseTest(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.mkdtemp()
        self.versionless_file = os.path.join(tmpdir, "packages.xml")
        self.fullpath = os.path.join(tmpdir, "bak", "packages.xml")
        os.makedirs(self.fullpath)
        self.schemas = os.path.join(self.fullpath, "packages.xml_swinstall_stack")

        with open(self.schemas,'w') as fh:
            fh.write(STACK)

        tree = ET.parse(self.schemas)
        root = tree.getroot()
        # we do this so that we dont raise an exception when instantiating
        SchemaBase.schema_version = DEFAULT_SCHEMA
        self.base = SchemaBase(root)

    def tearDown(self):
        os.remove(self.schemas)
        os.rmdir(self.fullpath)
        del self.base

    def test_root_dirname(self):
        root_dirname = self.base.root_dirname()
        expect = "/dd/facility/etc/bak/packages.xml"
        self.assertEqual(root_dirname, expect)

    def test_versionless_filename(self):
        versionless = self.base.versionless_filename()
        expect = "packages.xml"
        self.assertEqual(versionless, expect)

    def test_swinstall_stack_prop(self):
        schemas = self.base.schemas
        expect = "/dd/facility/etc/bak/packages.xml/packages.xml_swinstall_stack"
        self.assertEqual(schemas, expect)

    def test_root_prop(self):
        root = self.base.root
        expect = ET.Element('stack_history', {"path": "/dd/facility/etc/bak/packages.xml/packages.xml_swinstall_stack"})
        self.assertTrue(elems_equal(root, expect))

def elems_equal(e1, e2):
    """Test that two ElementTree.Element are equal"""
    if e1.tag == e2.tag and e1.attrib == e2.attrib:
        return True
    return False