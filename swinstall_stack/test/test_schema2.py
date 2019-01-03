#initialize testing environment
import env
# library imports
from datetime import datetime
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
# local imports
from swinstall_stack.schemas.schema2 import Schema2
from swinstall_stack.schemas.schema2.file_metadata import FileMetadata
from swinstall_stack.utils import datetime_from_str

STACK='''<?xml version="1.0" encoding="UTF-8"?>
<stack_history path="{}" schema="2">
   <elt action="install" datetime="20180702-144204" hash="194f835569a79ba433" version="3"/>
   <elt action="install" datetime="20180101-103813" hash="c94f6266789a483a43" version="2"/>
   <elt action="install" datetime="20171106-104603" hash="294fc86579b14b7d39" version="1"/>
</stack_history>
'''

class Schema2Test(unittest.TestCase):
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
        self.schema = Schema2(root, datetime.now())

    def tearDown(self):
        os.remove(self.schemas)
        os.rmdir(self.fullpath)
        del self.schema

    def test_current(self):
        current = self.schema.current()
        expected = FileMetadata(self.schema._versioned_file("3"),
                                 "install",
                                 "3",
                                 "20180702-144204",
                                 "194f835569a79ba433")
        self.assertEqual(current, expected)

    def test_current_false(self):
        current = self.schema.current()
        expected = FileMetadata(self.schema.root_dirname(),
                                 "install",
                                 "4",
                                 "20180702-144204",
                                 "194f835569a79ba433")
        self.assertNotEqual(current, expected)

    def test_next_version(self):
        """Get the next version number"""
        answer = self.schema.next_version()
        expected = 4
        self.assertEqual(answer, expected)

    def test_next_version_after_rollback(self):
        self.schema.rollback_element()
        answer = self.schema.next_version()
        expected = 4
        self.assertEqual(answer, expected)

    def test_current_version(self):
        answer = self.schema.current_version()
        expected = 3
        self.assertEqual(answer, expected)

    def test_version(self):
        answer = self.schema.version(1)
        expected = FileMetadata(self.schema._versioned_file("1"),
                                 "install",
                                 "1",
                                 "20171106-104603",
                                 "294fc86579b14b7d39")
        self.assertEqual(answer,expected)

    def test_version_nomatch(self):
        with self.assertRaises(KeyError):
            self.schema.version(10)

    def test_insert_element(self):
        fake_datetime = "20181216-124101"
        fake_hash = "123456789"
        self.schema.insert_element(fake_hash, datetime_from_str(fake_datetime))
        current = self.schema.current()
        expected = FileMetadata(self.schema._versioned_file("4"),
                                 "install",
                                 "4",
                                 fake_datetime,
                                 fake_hash)
        self.assertEqual(current, expected)

    def test_insert_element_with_revision(self):
        fake_datetime = "20181216-124101"
        fake_hash = "123456789"
        fake_revision = "r1324145"
        self.schema.insert_element(fake_hash, datetime_from_str(fake_datetime), fake_revision)
        current = self.schema.current()
        expected = FileMetadata(self.schema._versioned_file("4"),
                                 "install",
                                 "4",
                                 fake_datetime,
                                 fake_hash,
                                 fake_revision)
        self.assertEqual(current, expected)

    def test_rollback_element(self):
        # rollback 1
        self.schema.rollback_element()
        answer = self.schema.current_version()
        expected = 2
        self.assertEqual(answer, expected)
        # secon rollback
        self.schema.rollback_element()
        answer = self.schema.current_version()
        self.assertEqual(answer, 1)

    def test_too_many_rollbacks(self):
        self.schema.rollback_element()
        self.schema.rollback_element()
        with self.assertRaises(KeyError):
            self.schema.rollback_element()

    def test_file_on(self):
        # provide the current timestamp and make sure that we get back the
        # current FileMetadata instance
        test_datetime = datetime_from_str("20180702-144204")

        file_on = self.schema.file_on(test_datetime)

        expect = os.path.join(self.fullpath, "packages.xml_3")
        self.assertEqual(file_on.path, expect)

    def test_file_on_str(self):
        """The previous test should also work by supplying a string in the appropriate
        datetime format"""
        test_datetime = "20180702-144204"

        file_on = self.schema.file_on(test_datetime)

        expect = os.path.join(self.fullpath, "packages.xml_3")
        self.assertEqual(file_on.path, expect)

    def test_file_on_str_inbetween(self):
        """Test a timestamp that is inbetween the current timestamp and the previous
        timestamp. This should yield the previous timestamp"""
        test_datetime = "20180702-124204"

        file_on = self.schema.file_on(test_datetime)

        expect = os.path.join(self.fullpath, "packages.xml_2")
        self.assertEqual(file_on.path, expect)

    def test_file_on_nomatch(self):
        with self.assertRaises(LookupError):
            self.schema.file_on("20001010-111111")

if __name__ == '__main__':
    unittest.main()