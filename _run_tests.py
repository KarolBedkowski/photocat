#!/usr/bin/python
import os
import sys
import unittest


import sys
reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except:
	sys.setdefaultencoding("utf-8")


class KTestUnitRunner:

	class _SilentStream:
		def write(self, arg):
			pass
	
	def __init__(self, dir, result_filename='unit_test_results.txt', mask=None):
		self.__main_dir = dir
		self.__result_filename = os.path.join(os.path.realpath(dir), result_filename)
		self.__mask = mask

		self.__root = None
		self.__module_path = None
		self.__tests = []

		result_file = None
		self.__errors_count = 0
		self.__failures_count = 0
		self.__test_count = 0


	def run(self):
		self.__find_root()
		self.__find_tests()
		
		os.chdir(self.__root)
		sys.path.append(self.__root)

		results = []
		
		for test in self.__tests:
			result, count, errors = self.__run_test(test)
			results.append((test, result, count, errors))
			result_failures_count, result_errors_count = len(result.failures), len(result.errors)
			self.__failures_count += result_failures_count
			self.__errors_count += result_errors_count

			
		self.__save_results(results)
		
		print '\n***********************************************\n'
		print 'Result:  tests=%d,\tfailures=%d,\terrors=%d\n' % (self.__test_count,
				self.__failures_count, self.__errors_count)
	

	def __write_error(self, result_file, testcase, message):
		result_file.write('  TestCase: %s\n' % str(testcase))
		result_file.write('\n'.join([ '\t'+line for line in message.split('\n') ]))
		result_file.write('\n\n')


	def __save_results(self, results):
		result_file = open(self.__result_filename, 'w')

		result_file.write('Sumary:\t%2d tests,\t%2d failures,\t%2d errors\n\n' % 
				(self.__test_count, self.__failures_count, self.__errors_count))
		
		for test, result, tests_count, errors in results:
			result_file.write('Module:\t%-25s\t%2d tests\t' % (test, tests_count))
			if result.wasSuccessful():
				result_file.write('Successfull\n')
			else:
				result_file.write('** Fail ** \t%2d failures, %2d errors\n'
						% (len(result.failures), len(result.errors)))
			
		result_file.write('\n-----------------------------------------\n')
		
		for test, result, tests_count, errors in results:
			if not result.wasSuccessful() or errors is not None:
				result_file.write('Module:\t%s\t%2d tests, %2d failures, %2d errors\n\n' 
						% (test, tests_count, len(result.failures), len(result.errors)))

				if errors is not None:
					result_file.write('***** Error: %s\n' % str(errors))
				
				result_failures_count, result_errors_count = len(result.failures), len(result.errors)
				if result_failures_count > 0:
					result_file.write('** Failures: %d\n' % result_failures_count)
					[ self.__write_error(result_file, tc, res) for tc, res in result.failures ]

				if result_errors_count > 0:
					result_file.write('*** Errors: %d\n' % result_errors_count)
					[ self.__write_error(result_file, tc, res) for tc, res in result.errors ]

				result_file.write('-----------------------------------------\n')

		result_file.close()
		

	def __find_root(self):
		self.__root = os.path.realpath(self.__main_dir)
		module_path = []
		while self.__root != '':
			if not os.path.exists(os.path.join(self.__root, '__init__.py')):
				break
			module_path.insert(0, os.path.basename(self.__root))
			self.__root = os.path.dirname(self.__root)

		self.__module_path = '.'.join(module_path)


	def __add_file_to_tests(self, args, path, files):
		tests = [ name[:-3] for name in files if name.endswith('_test.py') and not name.startswith('_')]
		if len(tests) > 0:
			if path.startswith('.'): path = path[2:]
			module_path = self.__module_path + '.'.join(path.split(os.path.sep))
			[ self.__tests.append(module_path + '.' + name) for name in tests ]


	def __find_tests(self):
		os.path.walk(self.__main_dir, self.__add_file_to_tests, None)


	def __run_test(self, module_name):
		alltests = unittest.TestSuite()
		loader = unittest.TestLoader()
		count = 0
		print module_name,
		errors = None
		try:
			tc = loader.loadTestsFromName(module_name)
			alltests.addTest(tc)
			count += tc.countTestCases()
		except Exception, e:
			print e
			errors = e

		print '%d test cases' % count
		self.__test_count += count
		
		runner = unittest.TextTestRunner(verbosity=0, descriptions=1, stream=self._SilentStream())
		result = runner.run(alltests)
		return (result, count, errors)



if __name__ == '__main__':
	KTestUnitRunner('.').run()

