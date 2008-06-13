# -*- coding: utf-8 -*-
'''
$Id$
'''

__revision__ = '0.1'

import re
import gettext
_ = gettext.gettext


class SimpleValidator:
	def __init__(self, error_message=''):
		self._error_message = error_message

	def validate(self, value):
		return True

	def get_error(self):
		return self._error_message

	def convert_value_from_window(self, input_value):
		return input_value



class NotEmptyValidator(SimpleValidator):
	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _('Field must by not empty')

		SimpleValidator.__init__(self, error_message)

	def validate(self, value):
		return value is not None and len(value) > 0



class MinLenValidator(SimpleValidator):
	def __init__(self, min_len, error_message=None):
		if error_message is None:
			error_message = _('Too few characters in fields')

		SimpleValidator.__init__(self, error_message)
		self._min_len = min_len

	def validate(self, value):
		return len(value) >= self._min_len



class MaxLenValidator(SimpleValidator):
	def __init__(self, max_len, error_message=None):
		if error_message is None:
			error_message = _('Too many characters in fields')

		SimpleValidator.__init__(self, error_message)
		self._max_len = max_len

	def validate(self, value):
		return len(value) <= self._max_len



class ReValidator(SimpleValidator):
	def __init__(self, retext, error_message=None):
		if error_message is None:
			error_message = _('Incorrect value')

		SimpleValidator.__init__(self, error_message)
		self._retext = retext

	def validate(self, value):
		return re.match(self._retext, value) is not None



class IntValidator(SimpleValidator):
	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _('Integer value required')

		SimpleValidator.__init__(self, error_message)

	def validate(self, value):
		try:
			intval = int(value)
		except:
			return False
		else:
			return True

	def convert_value_from_window(self, input_value):
		return int(input_value)



class FloatValidator(SimpleValidator):
	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _('Float value required')

		SimpleValidator.__init__(self, error_message)

	def validate(self, value):
		try:
			intval = float(value)
		except:
			return False
		else:
			return True

	def convert_value_from_window(self, input_value):
		return float(input_value)



class TimeValidator(SimpleValidator):
	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _("Time isn't in correct format - HH:MM format required")

		SimpleValidator.__init__(self, error_message)

	def validate(self, value):
		if value is None or value == '':
			return True
		try:
			m = re.match(r'^(\d+):(\d\d)$', value)
			if int(m.group(2)) > 59:
				raise Exception('zła wartość')
		except Exception, err:
			return False
		else:
			return True



class DateValidator(SimpleValidator):
	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _("Date isn't in correct format - YYYY-MM-DD format required")

		SimpleValidator.__init__(self, error_message)

	def validate(self, value):
		if value is None or value == '':
			return True
		try:
			m = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$', value)
			if int(m.group(2)) > 12:
				raise Exception('zła wartość')
			if int(m.group(3)) > 32:
				raise Exception('zła wartość')
		except Exception, err:
			return False
		else:
			return True




# vim: encoding=utf8: ff=unix:
