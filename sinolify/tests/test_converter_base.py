from sinolify.utils.package import Package
from sinolify.converters.base import ConverterBase
from sinolify.utils.log import log

import logging
import os.path
from unittest import TestCase


class TestConverterBase(TestCase):
    def setUp(self) -> None:

        log.setLevel(logging.DEBUG)
        self.dummy_file = os.path.abspath(__file__)

        self.source = Package(id='source')
        self.source.add(self.dummy_file, 'main/file1')
        self.source.add(self.dummy_file, 'main/file2c.c')
        self.source.add(self.dummy_file, 'main/file3.txt')
        self.source.add(self.dummy_file, 'other/file7')

        self.target = Package(id='target')
        self.converter = ConverterBase(source=self.source, target=self.target)
        super().setUp()


    def test_find(self):
        self.assertEqual({'main/file1', 'other/file7'},
                         set(self.converter.find(r'.*file\d+[a-z]*')))
        self.assertEqual(set(self.converter.find(r'.*file\d+[a-z]*(\.[a-z]*)?')),
                         set(self.converter.find('.*')))

    def test_ignore(self):
        self.converter.ignore('main/.*')
        self.assertEqual({'other/file7'}, self.converter.not_processed())

    def test_copy(self):
        self.converter.ignore('main/file3.*')
        self.assertEqual(1, self.converter.copy(r'main/.*', transform=(lambda p: p + '.copied'),
                                condition=(lambda p: '1' not in p), ignore_processed=True))
        self.assertEqual({'main/file2c.c.copied'},
                         set(self.target.find('.*')))
        self.assertEqual(2, self.converter.copy(r'main/.*', transform=(lambda p: p + '.copied2'),
                                             condition=(lambda p: '1' not in p)))
        self.assertEqual({'main/file2c.c.copied', 'main/file2c.c.copied2', 'main/file3.txt.copied2'},
                         set(self.target.find('.*')))

    def test_copy_rename(self):
        self.assertEqual(4, self.converter.copy_rename('(.*/)file(.*)', r'\1renamed\2'))
        self.assertEqual({'other/renamed7', 'main/renamed3.txt', 'main/renamed1', 'main/renamed2c.c'},
                         set(self.target.find('.*')))

    def test_not_processed(self):
        self.converter.ignore(r'main/.*')
        self.assertEqual({'other/file7'}, self.converter.not_processed())

