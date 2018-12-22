#initialize testing environment
import env
# imports
import os
import tempfile
import unittest
from datetime import date, time, datetime
import xml.etree.ElementTree as ET
from swinstall_stack.schemas.schema2 import (Schema2, FileMetadata)
from swinstall_stack.utils import datetime_from_str
from swinstall_stack.constants import DEFAULT_SCHEMA, ELEM

STACK='''<?xml version="1.0" encoding="UTF-8"?>
<stack_history path="{}" schema="2">
   <elt action="install" date_time="20180702-144204" hash_value="194f835569a79ba433" version="3"/>
   <elt action="install" date_time="20180101-103813" hash_value="c94f6266789a483a43" version="2"/>
   <elt action="install" date_time="20171106-104603" hash_value="294fc86579b14b7d39" version="1"/>
</stack_history>
'''

class TestFileMetadataWithSwinstallStackFile(unittest.TestCase):
    """These tests require swisntall_stack file to exist so we build one
    in setUp and tear it down afterwards in (you guessed it) tearDown"""
    def setUp(self):
        tmpdir = tempfile.mkdtemp()
        self.versionless_file = os.path.join(tmpdir, "packages.xml")
        self.fullpath = os.path.join(tmpdir, "bak", "packages.xml")
        os.makedirs(self.fullpath)
        self.schemas = os.path.join(self.fullpath, "packages.xml_swinstall_stack")

        with open(self.schemas,'w') as fh:
            fh.write(STACK.format(self.schemas))

        tree = ET.parse(self.schemas)
        root = tree.getroot()
        self.schema = Schema2(root)

    def tearDown(self):
        os.remove(self.schemas)
        os.rmdir(self.fullpath)
        del self.schema

    def test_is_current(self):
        version_path = os.path.join(self.fullpath, "packages.xml_3")
        metadata = FileMetadata(version_path, "install", "3", "20180702-144204", "194f835569a79ba433" )
        self.assertTrue(metadata.is_current())

    def test_is_current_false(self):
        version_path = os.path.join(self.fullpath, "packages.xml_2")
        metadata = FileMetadata(version_path, "install", "2", "20180101-103813", "c94f6266789a483a43" )
        self.assertFalse(metadata.is_current())


class TestFileMetadata(unittest.TestCase):

    def setUp(self):
        self.fullpath = os.path.join("dd","facility","etc", "bak", "packages.xml")

    def test_path_prop(self):
        version_path = os.path.join(self.fullpath, "packages.xml_2")
        metadata = FileMetadata(version_path, "install", "2", "20180101-103813", "c94f6266789a483a43" )
        self.assertEqual(metadata.path, version_path)

    def test_versionlesspath_prop(self):
        version_path = os.path.join(self.fullpath, "packages.xml_2")
        metadata = FileMetadata(version_path, "install", "2", "20180101-103813", "c94f6266789a483a43" )
        versionless_path = "/dd/facility/etc/packages.xml"
        self.assertEqual(metadata.versionless_path, versionless_path)

    def test_action_prop(self):
        version_path = os.path.join(self.fullpath, "packages.xml_2")
        metadata = FileMetadata(version_path, "install", "2", "20180101-103813", "c94f6266789a483a43" )
        self.assertEqual(metadata.action, "install")

    def test_version_prop(self):
        version_path = os.path.join(self.fullpath, "packages.xml_2")
        metadata = FileMetadata(version_path, "install", "2", "20180101-103813", "c94f6266789a483a43" )
        self.assertEqual(metadata.version, 2)


    def test_date_time_prop(self):
        version_path = os.path.join(self.fullpath, "packages.xml_2")
        metadata = FileMetadata(version_path, "install", "2", "20180101-103813", "c94f6266789a483a43" )
        self.assertEqual(metadata.date_time, datetime_from_str("20180101-103813"))

if __name__ == '__main__':
    unittest.main()
