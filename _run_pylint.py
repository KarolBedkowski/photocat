#!/usr/bin/python
import sys, os
from pylint import lint
from pylint.reporters.html import HTMLReporter

import psyco
psyco.full()

IGNORE=['setup.py', 'run_tests.py']

sys.path.append('..')

import wx

class App(wx.App):
	def OnInit(self):
		"""
		OnInit
		"""
		wx.InitAllImageHandlers()

		process_dir('sag3')
		
		return True



def process_dir(dir):
	print "\nDir: ", dir
	os.chdir(dir)
	
	for file in [ o for o in os.listdir('.') 
			if o.endswith('.py') and not o.endswith('_test.py') and not o in IGNORE 
				and not o.startswith('doc') ]:
		print ('%s...' % file).ljust(25),
		
		filedate = os.path.getmtime(file)	
		try:
			htmldate = os.path.getmtime('%s_pylint.html' % file)
		except:
			htmldate = -1
			
		if filedate > htmldate or os.path.getsize('%s_pylint.html' % file) == 0:
			output = open('%s_pylint.html' % file, 'w')
			lint.Run(['-i', 'y', file], HTMLReporter(output))
			output.close()
			print ' ok'
		else:
			print ' skip'
			
	for subdir in [ o for o in os.listdir('.') if os.path.isdir(o) and not o.startswith('.') ]:
		process_dir(subdir)
		os.chdir('..')
	

if __name__ == '__main__':
	app = App(None)
	app.MainLoop()
	print 'Done'

