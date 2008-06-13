#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

import unittest

from kpylibs.formaters import *

class TestFormaters(unittest.TestCase):
	def test_01_format_value_simple(self):
		self.assertEqual(format_size(12,		separate=True),	'12')
		self.assertEqual(format_size(123,		separate=True),	'123')
		self.assertEqual(format_size(1234,		separate=True),	'1 234')
		self.assertEqual(format_size(12345,		separate=True),	'12 345')
		self.assertEqual(format_size(123456,	separate=True),	'123 456')
		self.assertEqual(format_size(1234567,	separate=True),	'1 234 567')

	def test_02_format_value_human_1000(self):
		self.assertEqual(format_size(12,		True, 1000), '12')
		self.assertEqual(format_size(123,		True, 1000), '123')
		self.assertEqual(format_size(1234,		True, 1000), '1k')
		self.assertEqual(format_size(12345,		True, 1000), '12k')
		self.assertEqual(format_size(123456,	True, 1000), '123k')
		self.assertEqual(format_size(1234567,	True, 1000), '1m')
		self.assertEqual(format_size(12345678,	True, 1000), '12m')
		self.assertEqual(format_size(123456789,	True, 1000), '123m')
		self.assertEqual(format_size(1234567890,	True, 1000), '1g')

	def test_03_format_value_human_1024(self):
		self.assertEqual(format_size(12,		True), '12')
		self.assertEqual(format_size(123,		True), '123')
		self.assertEqual(format_size(1234,		True), '1k')
		self.assertEqual(format_size(12345,		True), '12k')
		self.assertEqual(format_size(123456,	True), '120k')
		self.assertEqual(format_size(1234567,	True), '1m')
		self.assertEqual(format_size(12345678,	True), '11m')
		self.assertEqual(format_size(123456789,	True), '117m')
		self.assertEqual(format_size(1234567890,	True), '1g')

	def test_04_format_value_human_reduce(self):
		self.assertEqual(format_size(12,		True, 1000, reduce_at=1000000), '12')
		self.assertEqual(format_size(123,		True, 1000, reduce_at=1000000), '123')
		self.assertEqual(format_size(1234,		True, 1000, reduce_at=1000000), '1234')
		self.assertEqual(format_size(12345,		True, 1000, reduce_at=1000000), '12345')
		self.assertEqual(format_size(123456,	True, 1000, reduce_at=1000000), '123456')
		self.assertEqual(format_size(1234567,	True, 1000, reduce_at=1000000), '1234k')
		self.assertEqual(format_size(12345678,	True, 1000, reduce_at=1000000), '12345k')
		self.assertEqual(format_size(123456789,	True, 1000, reduce_at=1000000), '123456k')
		self.assertEqual(format_size(1234567890,	True, 1000, reduce_at=100000), '1234m')

	def test_05_format_value_human_reduce_separate(self):
		self.assertEqual(format_size(12,		True, 1000, reduce_at=1000000, separate=True), '12')
		self.assertEqual(format_size(123,		True, 1000, reduce_at=1000000, separate=True), '123')
		self.assertEqual(format_size(1234,		True, 1000, reduce_at=1000000, separate=True), '1 234')
		self.assertEqual(format_size(12345,		True, 1000, reduce_at=1000000, separate=True), '12 345')
		self.assertEqual(format_size(123456,	True, 1000, reduce_at=1000000, separate=True), '123 456')
		self.assertEqual(format_size(1234567,	True, 1000, reduce_at=1000000, separate=True), '1 234k')
		self.assertEqual(format_size(12345678,	True, 1000, reduce_at=1000000, separate=True), '12 345k')
		self.assertEqual(format_size(123456789,	True, 1000, reduce_at=1000000, separate=True), '123 456k')
		self.assertEqual(format_size(1234567890,	True, 1000, reduce_at=100000, separate=True), '1 234m')
		
	def test_06_format_value_format_simple(self):
		self.assertEqual(format_size(12,		separate=True, format="%2.02f"),	'12.00')
		self.assertEqual(format_size(123.32,	separate=True, format="%2.02f"),	'123.32')
		self.assertEqual(format_size(1234.32,	separate=True, format="%2.01f"),	'1 234.3')
		self.assertEqual(format_size(12345.19,	separate=True, format="%2.01f"),	'12 345.2')
		self.assertEqual(format_size(123456.23,	separate=False, format="%5.01f"),	'123456.2')
		self.assertEqual(format_size(1234567.2,	separate=False, format="%09d"),	'001234567')

	def test_07_format_value_format_human_1000(self):
		self.assertEqual(format_size(12,		True, 1000, format="%2.02f"), '12.00')
		self.assertEqual(format_size(123,		True, 1000, format="%2.02f"), '123.00')
		self.assertEqual(format_size(1234,		True, 1000, format="%2.02f"), '1.23k')
		self.assertEqual(format_size(12345,		True, 1000, format="%2.02f"), '12.35k')
		self.assertEqual(format_size(123456,	True, 1000, format="%2.02f"), '123.46k')
		self.assertEqual(format_size(1234567,	True, 1000, format="%2.02f"), '1.23m')
		self.assertEqual(format_size(12345678,	True, 1000, format="%2.02f"), '12.35m')
		self.assertEqual(format_size(123456789,	True, 1000, format="%2.02f"), '123.46m')
		self.assertEqual(format_size(1234567890,	True, 1000, format="%2.02f"), '1.23g')

	def test_08_format_upper(self):
		self.assertEqual(format_size(12,		True, upper=True), '12')
		self.assertEqual(format_size(123,		True, upper=True), '123')
		self.assertEqual(format_size(1234,		True, upper=True), '1K')
		self.assertEqual(format_size(12345,		True, upper=True), '12K')
		self.assertEqual(format_size(123456,	True, upper=True), '120K')
		self.assertEqual(format_size(1234567,	True, upper=True), '1M')
		self.assertEqual(format_size(12345678,	True, upper=True), '11M')
		self.assertEqual(format_size(123456789,	True, upper=True), '117M')
		self.assertEqual(format_size(1234567890,	True, upper=True), '1G')

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromName(__name__)
	unittest.TextTestRunner(verbosity=9).run(suite)

