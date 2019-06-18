import unittest
import unittest.mock

from dirguard import *

class MyTest(unittest.TestCase):
    def test_setup(self):
        self.assertEqual(3, 1 + 2)


    def test_dir_size(self):
        self.assertEqual(100, dir_size(
            (DirEntry('a', 30, 111), DirEntry('b', 69, 112), DirEntry('c', 1, 113))))
        self.assertEqual(100, dir_size(
            (DirEntry('a', 31, 111), DirEntry('b', 69, 112), DirEntry('c', 0, 113))))


    def test_dir_entry_count(self):
        self.assertEqual(3, dir_entry_count(
            (DirEntry('a', 30, 111), ('b', 69, 112), ('c', 1, 113))))
        self.assertEqual(1, dir_entry_count(
            (DirEntry('a', 30, 111),)))
        self.assertEqual(0, dir_entry_count((())))


    def test_oldest_entry(self):
        self.assertEqual(1, oldest_entry(
            (DirEntry('a', 30, 200), DirEntry('b', 20, 100), DirEntry('c', 42, 300))))
        self.assertEqual(0, oldest_entry(
            (DirEntry('a', 30, 0), DirEntry('b', 20, 100), DirEntry('c', 42, 300))))
        self.assertEqual(2, oldest_entry(
            (DirEntry('a', 30, 200), DirEntry('b', 20, 100), DirEntry('c', 42, 10))))


    def test_delete_oldest_entry(self):
        dir_list = [DirEntry('a', 30, 200), DirEntry('b', 20, 100), DirEntry('c', 42, 400)]
        dir_list_copy = dir_list[:]
        self.assertEqual(3, dir_entry_count(dir_list))
        file_deleter = unittest.mock.MagicMock()
        delete_oldest_entry(dir_list, file_delete_fun=file_deleter)
        file_deleter.assert_called_with(dir_list_copy[1])
        self.assertEqual(2, dir_entry_count(dir_list))


    def test_delete_oldest_entry_empty(self):
        dir_list = []
        self.assertEqual(0, dir_entry_count(dir_list))
        file_deleter = unittest.mock.MagicMock()
        delete_oldest_entry(dir_list, file_delete_fun=file_deleter)
        self.assertEqual(0, file_deleter.call_count)
        self.assertEqual(0, dir_entry_count(dir_list))


    def test_cleanup_for_size_simple(self):
        dir_list = [DirEntry('a', 30, 200), DirEntry('b', 20, 100), DirEntry('c', 42, 400)]
        self.assertEqual(30 + 20 + 42, dir_size(dir_list))
        cleanup_for_size(dir_list, 60)
        self.assertEqual(42, dir_size(dir_list))

        cleanup_for_size(dir_list, 60)
        self.assertEqual(42, dir_size(dir_list))

        cleanup_for_size(dir_list, 10)
        self.assertEqual(0, dir_size(dir_list))

        cleanup_for_size(dir_list, 10)
        self.assertEqual(0, dir_size(dir_list))


    def test_cleanup_for_entry_count_simple(self):
        dir_list = [DirEntry('a', 30, 200), DirEntry('b', 20, 100), DirEntry('c', 42, 400)]
        self.assertEqual(3, dir_entry_count(dir_list))
        cleanup_for_entry_count(dir_list, 1000)
        self.assertEqual(3, dir_entry_count(dir_list))

        cleanup_for_entry_count(dir_list, 2)
        self.assertEqual(2, dir_entry_count(dir_list))
        self.assertEqual("a", dir_list[0].name)
        self.assertEqual("c", dir_list[1].name)

        cleanup_for_entry_count(dir_list, 1)
        self.assertEqual(1, dir_entry_count(dir_list))
        self.assertEqual("c", dir_list[0].name)


    def test_make_dir_list_from_directory(self):
        # A very, very, minimal test, indeed.
        self.assertTrue(make_dir_list_from_directory('/tmp/'))
