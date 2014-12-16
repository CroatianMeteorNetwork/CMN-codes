# Copyright 2014 Denis Vida, denis.vida@gmail.com

# The antialisaing_test is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, version 2.

# The antialisaing_test is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the antialisaing_test; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as img

n_antialias = 1 #Aliasing setting
antialias_weigh = 5

def get_coords(x, y, max_col, max_row, n):
	n_range = 2*n+1
	coord_list = []
	for i in range(0, n_range):
		for j in range(0, n_range):
			x_dim = x+i-n
			y_dim = y+j-n

			x_dim = 0 if x_dim<0 else x_dim
			y_dim = 0 if y_dim<0 else y_dim

			x_dim = max_col-1 if x_dim>=max_col else x_dim
			y_dim = max_row-1 if y_dim>=max_row else y_dim

			coord_list.append((x_dim, y_dim))

	return set(coord_list)

im = img.open("test.jpg")
im = im.convert('L')
img_array = np.array(im)


nrows = len(img_array)
ncols = len(img_array[0])

antialiased_img = np.zeros(shape=(nrows,ncols))

for row in range(0, nrows):
	for col in range (0, ncols):
		s = 0
		n_size = (2*n_antialias+1)**2
		for x, y in get_coords(row, col, nrows, ncols, n_antialias):
			s += img_array[x][y]
		avg_val = (s+antialias_weigh*img_array[row][col]) / (n_size+antialias_weigh)
		antialiased_img[row][col] = avg_val

						




im = img.fromarray(antialiased_img)
im = im.convert('L')
#im.show()
im.save("antialiasing_test.jpg")