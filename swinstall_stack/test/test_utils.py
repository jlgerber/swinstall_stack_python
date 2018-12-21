from datetime import datetime, date, time
import unittest
# local imports
import env
from swinstall_stack.utils import *

class UtilsTest(unittest.TestCase):
    def test_datetime_from_str(self):
        dt_str = "20180811-221113"
        expected = datetime.combine(date(2018,8,11), time(22,11,13))
        self.assertEqual(datetime_from_str(dt_str), expected)

    def test_datetime_revision_from_str_no_rev(self):
        dt_str = "20180811-221113"
        expected = (datetime.combine(date(2018,8,11), time(22,11,13)), None)
        self.assertEqual(datetime_revision_from_str(dt_str), expected)


    def test_datetime_revision_from_str_with_rev(self):
        dt_str = "20180811-221113_r12345"
        expected = (datetime.combine(date(2018,8,11), time(22,11,13)), "r12345")
        self.assertEqual(datetime_revision_from_str(dt_str), expected)

    def test_datetime_to_str(self):
        dt = datetime.combine(date(2018,8,11), time(22,11,13))
        expected = "20180811-221113"
        self.assertEqual(datetime_to_str(dt), expected)


if __name__ == '__main__':
    unittest.main()