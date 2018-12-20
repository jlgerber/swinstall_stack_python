#initialize testing environment
import env
# imports
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from swtrack.swinstall_stack.schema2 import Schema2
from swtrack.swinstallfile import SwinstallFile
from swtrack.utils import datetime_from_str

STACK='''<?xml version="1.0" encoding="UTF-8"?>
<stack_history path="/Users/jonathangerber/src/python/swinstall_proposal/examples/schema2/bak/packages.xml/packages.xml_swinstall_stack" schema="2">
   <elt action="install" datetime="20180702-144204" hash="194f835569a79ba433" version="3"/>
   <elt action="install" datetime="20180101-103813" hash="c94f6266789a483a43" version="2"/>
   <elt action="install" datetime="20171106-104603" hash="294fc86579b14b7d39" version="1"/>
</stack_history>
'''

class Schema2Test(unittest.TestCase):
    def setUp(self):
        tmpfile = tempfile.mkstemp(text=True)
        # dont bother with lower level file handle
        os.close(tmpfile[0])
        self.swinstall_stack = tmpfile[1]
        with open(self.swinstall_stack,'w') as fh:
            fh.write(STACK)

        tree = ET.parse(self.swinstall_stack)
        root = tree.getroot()
        self.schema = Schema2(root)

    def tearDown(self):
        os.remove(self.swinstall_stack)
        del self.schema

    def test_current(self):
        current = self.schema.current()
        expected = SwinstallFile(self.schema.root_dirname(),
                                 "install",
                                 "3",
                                 "20180702-144204",
                                 "194f835569a79ba433")
        self.assertEqual(current, expected)

    def test_current_false(self):
        current = self.schema.current()
        expected = SwinstallFile(self.schema.root_dirname(),
                                 "install",
                                 "4",
                                 "20180702-144204",
                                 "194f835569a79ba433")
        self.assertNotEqual(current, expected)

    def test_next_version(self):
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
        expected = SwinstallFile(self.schema.root_dirname(),
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
        expected = SwinstallFile(self.schema.root_dirname(),
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
        expected = SwinstallFile(self.schema.root_dirname(),
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
        self.schema.rollback_element()
        answer = self.schema.current_version()
        self.assertEqual(answer, 1)

    def test_too_many_rollbacks(self):
        self.schema.rollback_element()
        self.schema.rollback_element()
        with self.assertRaises(KeyError):
            self.schema.rollback_element()

    def test_file_on(self):
        pass

if __name__ == '__main__':
    unittest.main()