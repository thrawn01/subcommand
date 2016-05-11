# -*- coding: utf-8 -*-

from __future__ import print_function

from subcommand import opt, noargs
import subcommand
import unittest


class CommandTest(subcommand.Commands):

    def __init__(self):
        subcommand.Commands.__init__(self)
        self.opt('-d', '--debug', action='store_const', const=True,
                 default=False, help="Output debug into to stdout")
        self._name = 'test'
        self.count = 0

    @opt('--count', default=1, type=int, help="Number of Hello's")
    @opt('name', help="Your name")
    def hello(self, name, count=1):
        for x in range(count):
            print('Hello, %s' % name)
            self.count += 1
        return 0

    @opt('--nodefault')
    def default(self, nodefault='spam'):
        return nodefault

    @noargs
    def return_non_zero(self):
        print('Exit with non-zero status')
        return 1


class TestSubCommandSimple(unittest.TestCase):

    def test_subcommand_parser_simple(self):
        test_command = CommandTest()
        parser = subcommand.SubParser([test_command], desc='testing')
        ret = parser.run(['test', 'hello', 'derrick', '--count', '5'])

        # Test the count sub command
        self.assertEqual(test_command.count, 5)
        self.assertEqual(ret, 0)

        # Test the non zero command
        self.assertEqual(parser.run(['test', 'return-non-zero']), 1)

    def test_command_parser_simple(self):
        test_command = CommandTest()
        parser = subcommand.Parser([test_command], desc='testing')
        ret = parser.run(['hello', 'derrick', '--count', '5'])

        # Test the count sub command
        self.assertEqual(test_command.count, 5)
        self.assertEqual(ret, 0)

        # Test the non zero command
        self.assertEqual(parser.run(['return-non-zero']), 1)


class TestSubCommandDefault(unittest.TestCase):

    def test_subcommand_default(self):
        test_command = CommandTest()
        parser = subcommand.Parser([test_command], desc='testing')
        ret = parser.run(['default'])

        self.assertEqual(ret, 'spam')

        ret = parser.run(['default', '--nodefault', 'eggs'])
        self.assertEqual(ret, 'eggs')
