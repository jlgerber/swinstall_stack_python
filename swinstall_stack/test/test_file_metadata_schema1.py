#initialize testing environment
import env
# imports
import os
import tempfile
import unittest
from datetime import date, time, datetime
import xml.etree.ElementTree as ET
from swinstall_stack.schemas.schema1.file_metadata import FileMetadata
from swinstall_stack.utils import datetime_from_str
from swinstall_stack.constants import DEFAULT_SCHEMA, ELEM


class TestFileMetadata(unittest.TestCase):

    def test_init_from_version_str(self): #(cls, path, is_current, version):
        version_str = "20181112-233000"
        expected_dt = datetime.combine(date(2018,11,12), time(23,30,0))
        path = "/dd/facility/etc/bak/packages.xml/packages.xml_{}".format(version_str)

        metadata = FileMetadata.init_from_version_str(path, "True", version_str)

        expect =FileMetadata(path, "True", expected_dt)
        self.assertEqual(metadata, expect)

    def test_extract_datetime_and_revision_str(self):
        version_str = "20181112-233000"

        dt,rev = FileMetadata._extract_datetime_and_revision(version_str)

        expected_dt = datetime.combine(date(2018,11,12), time(23,30,0))
        self.assertEqual(rev, None)
        self.assertEqual(dt, expected_dt)

    def test_extract_datetime_and_revision_str_w_revision(self):
        version_str = "20181112-233000_r12345"

        dt,rev = FileMetadata._extract_datetime_and_revision(version_str)

        expected_dt = datetime.combine(date(2018,11,12), time(23,30,0))
        expected_rev = "r12345"
        self.assertEqual(rev, expected_rev)
        self.assertEqual(dt, expected_dt)

    def test_extract_datetime_and_revision_datetime(self):
        expected_dt = datetime.combine(date(2018,11,12), time(23,30,0))

        dt,rev = FileMetadata._extract_datetime_and_revision(expected_dt)

        self.assertEqual(rev, None)
        self.assertEqual(dt, expected_dt)

if __name__ == '__main__':
    unittest.main()