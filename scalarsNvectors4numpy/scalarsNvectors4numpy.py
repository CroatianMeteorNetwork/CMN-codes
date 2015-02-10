# coding=utf-8
# Copyright 2015 Denis Vida, denis.vida@gmail.com

# The scalarsNvectors4numpy is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, version 2.

# The scalarsNvectors4numpy is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the scalarsNvectors4numpy ; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA


import numpy as np


def sinList(x):
	""" Take sine of a list and cut the list valies that are below 0.
	"""
	res = np.sin(x)
	res[res<0] = 0

	return res


def sinScalar(x):
	""" Take a sine of a scalar and cut the value to 0 if the sine is < 0.
	"""
	res = np.sin(x)
	if res < 0: 
		res = 0

	return np.array(res, copy=False, ndmin=1)


def universalDecorator(func, alt_func):
	""" Checks the first argument of a function, if it is an array_like, call the first function. 
		Otherwise if it is a scalar, call the second function. If it is none of the above, return [].
	"""

	def _inner(*args, **kwargs):
		# Check if first argument is an array_like or a scalar
		argument = args[0]

		# Convert set to list
		if isinstance(argument, (frozenset, set)):
			argument = list(argument)
			arg_list = list(args)
			arg_list.pop(0)
			arg_list.insert(0, argument)
			args = tuple(arg_list)

		if isinstance(argument, (np.ndarray, list, tuple)):
			return func(*args, **kwargs)
		elif np.isscalar(argument):
			return alt_func(*args, **kwargs)
		else:
			return np.array([])

	return _inner


# Decorated sine function for both vectors and scalars.
universalSin = universalDecorator(sinList, sinScalar)


## TEST BEHAVIOUR

temp_list = [3.2, 0.6, 1]
print 'List: ', universalSin(temp_list)
print 'Tuple: ', universalSin(tuple(temp_list))

print 'Numpy array: ', universalSin(np.array(temp_list))

# Warning: Order of elements is not preserved in sets!
print 'Set: ', universalSin(set(temp_list))
print 'Frozenet: ', universalSin(frozenset(temp_list))


print 'Scalar: ', universalSin(3.2)
print 'Scalar: ', universalSin(0.6)
print 'Scalar: ', universalSin(1)

print 'None: ', universalSin(None)

# Warning, bool types are interpreted as scalars! True = 1, False = 0
print 'Bool (True):', universalSin(True)
print 'Bool (False):', universalSin(False)

