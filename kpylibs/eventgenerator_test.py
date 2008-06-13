#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

import unittest

from kpylibs.eventgenerator import EventGenerator

class TestDbDatabase(unittest.TestCase):
	def test_01_create(self):
		evg = EventGenerator()
		self.assert_(evg is not None)
		del evg


	def test_02_add(self):
		def test1():	pass
		def test2():	pass

		evg = EventGenerator()
		self.assert_(evg.event_list('dsdsds') is None)

		evg.event_add_listener('test', test1)
		self.assertEqual(len(evg.event_list('test')), 1)
		evg.event_add_listener('test', test2)
		self.assertEqual(len(evg.event_list('test')), 2)

		evg.event_remove_listener('test', test1)
		self.assertEqual(len(evg.event_list('test')), 1)
		evg.event_remove_listener('test', test2)
		self.assert_(evg.event_list('test') is None)

	def test_03_call_01(self):
		self.a=0
		def test1():
			self.a += 1

		def test2():
			self.a += 3

		evg = EventGenerator()
		evg.event_add_listener('test1', test1)
		evg.event_add_listener('test1', test2)
		
		evg.event_call('test1')
		self.assertEqual(self.a, 4)


	def test_03_call_02(self):
		self.a=0
		def test1():
			self.a += 1

		def test2():
			self.a += 3

		evg = EventGenerator()
		evg.event_add_listener('test1', test1)
		evg.event_add_listener('test2', test2)
		
		evg.event_call('test1')
		self.assertEqual(self.a, 1)

		self.a = 0
		evg.event_call('test2')
		self.assertEqual(self.a, 3)


	def test_03_call_03(self):
		self.a=0
		def test1():
			self.a += 1

		def test2():
			self.a += 3

		evg = EventGenerator()
		evg.event_add_listener('test1', test1)
		evg.event_add_listener('test2', test2)
		
		evg.event_call('test1wewe')
		self.assertEqual(self.a, 0)


	def test_03_call_04(self):
		self.a = 0
		def test(b, c, f):
			self.a = (b, c, f)

		evg = EventGenerator()
		evg.event_add_listener('test', test)
		
		evg.event_call('test', (1), c=2, f=3)
		self.assertEqual(self.a, (1, 2, 3))





if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromName(__name__)
	unittest.TextTestRunner(verbosity=9).run(suite)

