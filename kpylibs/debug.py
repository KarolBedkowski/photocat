#!/usr/bin/python2.4
# -*- coding: utf8 -*-
"""
Misc debug func.
"""

__revision__ = '$Id$'

__all__ = ['debugd']


import logging



def debugd(func, *keys, **k):
	""" Dekoratow wyświetlający wartości parametrów i rezultat danej funkcji/metody
		via logging i gdy __debug__
	"""
	#retrieve the names of functionarguments via reflection:
	argnames = func.func_code.co_varnames[:func.func_code.co_argcount]

	#retrieve the name of the function itself:
	fname = func.func_name

	def echo(*args, **kwargs):
		"""instead of the original function, we return this echo function that
		calls the original one. This way, we can add additional behaviour:"""

		#call the original function and store the result:
		result = func(*args, **kwargs)

		if __debug__:
			#create a string that explains input, e.g: a=5, b=6
			in_str = ', '.join('%s = %r' % entry for entry in zip(argnames, args) + kwargs.items())

			#print input and output:
			logging.debug("%s: Input=%s Output=%s" % (fname, in_str, result))

		return result

	# the function returned has the name 'echo'.
	# this is not very representative, so we rename it
	# "<original function name> (debug echo)"
	echo.func_name = "%s (debug echo)" % func.func_name
	return echo



# vim: encoding=utf8: ff=unix:
