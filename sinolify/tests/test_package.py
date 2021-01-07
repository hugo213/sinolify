from unittest import TestCase
import os.path

from sinolify.utils.package import Package


class TestPackage(TestCase):
    def setUp(self):
        self.package = Package(id='test1')
        self.dummy_file = os.path.abspath(__file__)
        self.package.add(self.dummy_file, 'dir1/dir2/file')
        super().setUp()

    def test_id(self):
        self.assertEqual(self.package.id, 'test1')

    def test_root(self):
        self.assertTrue(os.path.exists(self.package.root))
        self.assertTrue(os.path.exists(os.path.join(self.package.root, 'dir1/dir2/file')))

    def test_abspath(self):
        self.assertTrue(os.path.exists(self.package.abspath('dir1/dir2/file')))

    def test_find(self):
        self.assertEqual(len(list(self.package.find(rf'file'))), 0)
        self.assertEqual(len(list(self.package.find(rf'.*file'))), 1)
        self.assertEqual(len(list(self.package.find(rf'.*fil'))), 0)
