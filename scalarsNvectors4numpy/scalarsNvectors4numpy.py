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


def universalDecorator(func):
    """ Checks the first argument of a function, if it is an array_like, call the given function. 
        Otherwise if it is a scalar, converts it to a list. If it is none of the above, return [].
    """

    def _replaceArgument(args, argument):
        arg_list = list(args)
        arg_list.pop(0)
        arg_list.insert(0, argument)
        args = tuple(arg_list)

        return args


    def _inner(*args, **kwargs):

        argument = args[0]

        if isinstance(argument, (frozenset, set)):
            # Convert set to list
            argument = list(argument)
            args = _replaceArgument(args, argument)

        elif np.isscalar(argument):
            # Convert scalar to list
            argument = [argument]
            args = _replaceArgument(args, argument)


        if isinstance(argument, (np.ndarray, list, tuple)):
            return func(*args, **kwargs)
        else:
            return np.array([])

    return _inner


@universalDecorator
def sinList(x):
    """ Take sine of a list and cut the list valies that are below 0.
    """
    res = np.sin(x)
    res[res<0] = 0

    return res


## TEST BEHAVIOUR

temp_list = [3.2, 0.6, 1]
print 'List: ', sinList(temp_list)
print 'Tuple: ', sinList(tuple(temp_list))

print 'Numpy array: ', sinList(np.array(temp_list))

# Warning: Order of elements is not preserved in sets!
print 'Set: ', sinList(set(temp_list))
print 'Frozenet: ', sinList(frozenset(temp_list))


print 'Scalar: ', sinList(3.2)
print 'Scalar: ', sinList(0.6)
print 'Scalar: ', sinList(1)

print 'None: ', sinList(None)

# Warning, bool types are interpreted as scalars! True = 1, False = 0
print 'Bool (True):', sinList(True)
print 'Bool (False):', sinList(False)

