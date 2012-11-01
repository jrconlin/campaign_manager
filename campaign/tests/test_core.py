import unittest2
import mock
import sys
import os
import campaign


class TestCore(unittest2.TestCase):

    @mock.Mock(sys)
    def test_self_diag_vers(self):
        sys.version_info.return_value = ['', '', [2, 4, 0]]
        self.assertRaises(Exception, campaign.self_diag)

    @mock.Mock(os)
    def test_self_diag_path(self):
        os.path.exists.return_value = False
        self.assertRaises(Exception, campaign.self_diag)

    def test_get_group(self):
        group = {'a.b': '1', 'b.c': 1}
        filtr = 'a'
        filtrd = campaign.get_group(filtr, group)
        self.assertFalse('b.c' in filtrd)
        self.assertEqual(group, campaign.get_group(None, group))
