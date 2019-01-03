#initialize testing environment
import env
# imports
from datetime import datetime
import os
import tempfile
import unittest
from datetime import datetime
import xml.etree.ElementTree as ET
from swinstall_stack.schemas.schema1 import Schema1
from swinstall_stack.schemas.schema1.file_metadata import FileMetadata
from swinstall_stack.utils import datetime_from_str
import logging
log = logging.getLogger(__name__)


STACK='''<stack_history path="{}">
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
        self.schemas = os.path.join(self.fullpath, "packages.xml_swinstall_stack")

        with open(self.schemas,'w') as fh:
            fh.write(STACK.format(self.schemas))

        tree = ET.parse(self.schemas)
        root = tree.getroot()
        self.schema = Schema1(root, datetime.now())

    def tearDown(self):
        os.remove(self.schemas)
        os.rmdir(self.fullpath)
        del self.schema

    # def test_parse(self):
    #     # we assert that this will not raise an exception
    #     Schema1.parse(self.versionless_file)

    def test_current(self):
        # grab the current file, retrieving a FileMetadata instance
        current = self.schema.current()

        expected = FileMetadata.init_from_version_str(
            self.schema._versioned_file("20181105-103813", None),
            "True",
            "20181105-103813")
        self.assertEqual(current, expected)

    def test_current_false(self):

        current = self.schema.current()

        expected = FileMetadata.init_from_version_str(
            self.schema._versioned_file("20180702-144204", None),
            "True",
            "20180702-144204")
        self.assertNotEqual(current, expected)

    def test_current_version(self):

        answer = self.schema.current_version()

        expected = datetime_from_str("20181105-103813")
        self.assertEqual(answer, expected)

    def test_version(self):

        answer = self.schema.version(datetime_from_str("20181102-144204"))

        expected = FileMetadata.init_from_version_str(self.schema._versioned_file("20181102-144204", None),
                                "False",
                                 "20181102-144204")

        self.assertEqual(answer, expected)

    def test_version_nomatch(self):
        with self.assertRaises(KeyError):
            self.schema.version("20171103-144204")

    def test_file_on_before_current(self):
        dt_str = "20181102-144204"
        dt = datetime_from_str(dt_str)

        result = self.schema.file_on(dt)

        expected = "{}/packages.xml_{}".format(self.schema.root_dirname(), dt_str)
        self.assertEqual(result.path, expected)

    def test_file_on_after_current(self):
        dt_str = "20181221-220000"
        dt = datetime_from_str(dt_str)

        result = self.schema.file_on(dt)

        expected = "{}/packages.xml_20181105-103813".format(self.schema.root_dirname())
        self.assertEqual(result.path, expected)

    def test_insert_element(self):
        fake_datetime = datetime_from_str("20181216-124101")

        self.schema.insert_element(fake_datetime)

        current = self.schema.current()
        expected = FileMetadata(self.schema._versioned_file(fake_datetime, None),
                                "True",
                                fake_datetime,
                                )
        self.assertEqual(current, expected)

    def test_insert_element_with_revision(self):
        fake_datetime = datetime_from_str("20181216-124101")
        fake_revision = "r1324145"

        self.schema.insert_element(fake_datetime, fake_revision)

        current = self.schema.current()
        expected = FileMetadata(self.schema._versioned_file(fake_datetime, fake_revision),
                                 "True",
                                 fake_datetime,
                                 fake_revision)
        self.assertEqual(current, expected)

    def test_rollback_element(self):
        # rollback 1
        self.schema.rollback_element(datetime.now())
        answer = self.schema.current_version()
        expected = datetime_from_str("20181102-144204")
        self.assertEqual(answer, expected)
        # rollback 2 - as far as we can go
        self.schema.rollback_element()
        answer = self.schema.current_version()
        expected = datetime_from_str("20161213-093146")
        self.assertEqual(answer, expected)

    def test_too_many_rollbacks(self):
        self.schema.rollback_element(datetime.now())
        self.schema.rollback_element(datetime.now())
        with self.assertRaises(IndexError):
            # there are two versions older than the current version. If
            # we try to roll back a third time, we should produce an
            # IndexError, as we try to use a negative index into root's
            # list of elements
            self.schema.rollback_element(datetime.now())

    def test_file_on(self):
        """provide the current timestamp and make sure that we get back the
        current FileMetadata instance"""
        test_datetime = datetime_from_str("20181105-103813")

        file_on = self.schema.file_on(test_datetime)

        expect = os.path.join(self.fullpath, "packages.xml_20181105-103813")
        self.assertEqual(file_on.path, expect)

    def test_file_on_str(self):
        """The previous test should also work by supplying a string in the appropriate
        datetime format"""
        test_datetime = "20181105-103813"

        file_on = self.schema.file_on(test_datetime)

        expect = os.path.join(self.fullpath, "packages.xml_20181105-103813")
        self.assertEqual(file_on.path, expect)

    def test_file_on_str_inbetween(self):
        """Test a timestamp that is inbetween the current timestamp and the previous
        timestamp. This should yield the previous timestamp"""
        test_datetime = "20181105-103812"

        file_on = self.schema.file_on(test_datetime)

        expect = os.path.join(self.fullpath, "packages.xml_20181102-144204")
        self.assertEqual(file_on.path, expect)

    def test_file_on_nomatch(self):
        with self.assertRaises(LookupError):
            self.schema.file_on("20001010-111111")



if __name__ == '__main__':
    unittest.main()
