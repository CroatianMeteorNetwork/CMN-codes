# Copyright 2015 Denis Vida, denis.vida@gmail.com

# The fireballFitter is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, version 2.

# The fireballFitter is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the fireballFitter; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA


from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np

def func(x, a, b, c, d, e, f):
    """ Define the function for fitting. """
    
    return a + b*x + c* np.exp(d*x) + e* np.exp(f*x)

def func_derive(x, a, b, c, d, e, f):
    """ Define the derivated function. """

    return b + c*d*np.exp(d*x) + e*f*np.exp(f*x)


def loadData(file_name):
    """ Loads input data from a given file into numpy arrays. Only First three columns are loaded. 
    The fourth column is optional and it contains data point weights. """

    t_data = []
    s_data = []
    h_data = []
    sigma_data = []

    for line in open(file_name).readlines():
        line = line.replace('\n', '')

        if not line:
            continue

        line = line.split()

        # Load data
        t_data.append(float(line[1]))
        s_data.append(float(line[2]))
        h_data.append(float(line[3]))

        # Check for weight data
        if len(line)>4:
            sigma_data.append(float(line[4]))

    t_data = np.array(t_data, dtype = np.float32)
    s_data = np.array(s_data, dtype = np.float32)
    h_data = np.array(h_data, dtype = np.float32)

    if sigma_data:
        sigma_data = np.array(sigma_data, dtype = np.float32)

    else:
        sigma_data = None

    

    return t_data, s_data, h_data, sigma_data

def saveCoeffs(coeff_list, file_name = 'exp_par.txt'):
    """ Saves coefficients to a file. """

    save_file = open(file_name, 'w')

    for i, coeff in enumerate(coeff_list):
        save_file.write('a' + str(i + 1) + ' = '+ str(coeff) + '\n')

    save_file.close()

def exportDataMaria(t_data, h_data, v_data, file_name='Alex.txt', point_precision=2):
    """ Exports data to format accepted by the Maria fireball software. """

    # Open file for writing
    export_file = open(file_name, 'w')

    # Write the number of points following
    n_data = int(len(t_data))

    export_file.write(str(n_data)+'\n\n')


    for i, time in enumerate(t_data):
        time = str(round(time, point_precision))
        height = str(round(h_data[i], point_precision))
        velocity = str(round(v_data[i], point_precision))

        export_file.write(time + ' ' + height + ' ' + velocity + '\n')

    export_file.close()



# INPUT FILE NAME
data_file = 'input.txt'

# Load data from a file
t_data, s_data, h_data, sigma_data = loadData(data_file)

## Fit s_data
# s_coeffs contains curve coeficients, p0 is the inital guess for the coeficients
s_coeffs, pcov = curve_fit(func, xdata = t_data, ydata = s_data, sigma = sigma_data, p0=(1, 1, 1, 1, 1, 1))

print 'Curve coefficients for s:', s_coeffs

# Save coefficients to a file
saveCoeffs(s_coeffs, 's_coeffs.txt')

# Plot data

## Plot s_data
plt.subplot(3, 1, 1)
plt.title('Fireball trajectory')

# Plot input data points (blue)
real_data = plt.scatter(t_data, s_data, s = 3, c = 'b', edgecolors='none')
plt.ylabel('Realtive path (km)')

# Plot fitted function points (red)
fitted_data = plt.scatter(t_data, func(t_data, *s_coeffs), s = 3, c = 'r', edgecolors='none')

#Plot the legend
plt.legend((real_data, fitted_data),
           ('Real data', 'Fitted data'),
           scatterpoints=1,
           loc='upper left',
           fontsize=10)


## Fit h_data
# h_coeffs contains curve coeficients, p0 is the inital guess for the coeficients
h_coeffs, pcov = curve_fit(func, xdata = t_data, ydata = h_data, sigma = sigma_data, p0=(1, 1, 1, 1, 1, 1))

print 'Curve coefficients for h:', h_coeffs

# Save coefficients to a file
saveCoeffs(h_coeffs, 'h_coeffs.txt')

## Plot h_data
plt.subplot(3, 1, 2)

# Plot input data points (blue)
real_data = plt.scatter(t_data, h_data, s = 3, c = 'b', edgecolors='none')

# Plot fitted function points (red)
fitted_data = plt.scatter(t_data, func(t_data, *h_coeffs), s = 3, c = 'r', edgecolors='none')
plt.ylabel('Height (km)')


## Plot velocity
plt.subplot(3, 1, 3)

# Calculate velocity
v_data = func_derive(t_data, *s_coeffs)
# Plot fitted function points (red)
velocity_data = plt.scatter(t_data, v_data, s = 3, c = 'g', edgecolors='none')
plt.ylabel('Velocity (km/s)')

#Plot the legend
plt.legend((velocity_data, ),
           ('Velocity (derived from path fit)', ),
           scatterpoints=1,
           loc='lower left',
           fontsize=10)


plt.xlabel('Time (s)')

# Export data to a file
exportDataMaria(t_data, h_data, v_data)

plt.show()