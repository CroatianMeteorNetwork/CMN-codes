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


# INPUT FILE NAME
data_file = 'input.txt'

# True = Use the 6-parameter fit for better ending approximation
# False = Use the 4-parameter fit for the whole flight path
extended_ending = True

# Sample the time domain at regular intervals
time_domain_sample = True
# Sample step (seconds)
time_sample_step = 0.2


from scipy.optimize import curve_fit, fsolve
import matplotlib.pyplot as plt
import numpy as np

def func(x, a, b, c, d):
    """ Define the exp function for fitting to fireball data. """
    
    return a + b*x + c* np.exp(d*x)

def funcExtend(x, a, b, c, d, e, f):
    """ Exp function with extended parameters for a better initial guess. """
    
    return a + b*x + c* np.exp(d*x) + e* np.exp(f*x)


def funcDerive(x, a, b, c, d):
    """ Define the derivated function. """

    return b + c*d*np.exp(d*x)

def funcExtendDerive(x, a, b, c, d, e, f):
    """ Exp function with extended parameters for a better initial guess. """
    
    return b + c * d * np.exp(d*x) + e * f * np.exp(f*x)

def func2ndDerive(x, a, b, c, d):
    """ Second derivative of the exp func. """

    return c * d*d * np.exp(d*x)

def funcExtend2ndDerive(x, a, b, c, d, e, f):
    """ Second derivative of the exp func. """

    return c * d*d * np.exp(d*x) + e * f*f* np.exp(f*x)


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
    # Normalize the beginning of t_data to 0
    t_data = t_data - min(t_data)

    s_data = np.array(s_data, dtype = np.float32)
    h_data = np.array(h_data, dtype = np.float32)

    if sigma_data:
        sigma_data = np.array(sigma_data, dtype = np.float32)

    else:
        sigma_data = np.ones_like(t_data)

    # # Sort data by time
    data = np.vstack((t_data, s_data, h_data, sigma_data)).T
    # Sort by first row (time)
    data = data[data[:,0].argsort()]
    # Split back to individual arrays
    t_data, s_data, h_data, sigma_data = np.vsplit(data.T, 4)
    t_data, s_data, h_data, sigma_data = t_data.T.ravel(), s_data.T.ravel(), h_data.T.ravel(), sigma_data.T.ravel()
    

    return t_data, s_data, h_data, sigma_data


def saveCoeffs(coeff_list, file_name = 'exp_par.txt', tx = None):
    """ Saves coefficients to a file. """

    save_file = open(file_name, 'w')

    if tx:
        save_file.write('tx = ' + str(tx) + '\n')

    for i, coeff in enumerate(coeff_list):
        save_file.write('a' + str(i + 1) + ' = '+ str(coeff) + '\n')

    save_file.close()


def exportDataMaria(t_data, h_data, v_data, file_name='Alex.txt', point_precision=2):
    """ Exports data to format accepted by the Maria fireball software. """

    # Make a list of lines to export
    export_lines = []

    for i, time in enumerate(t_data):
        velocity = round(v_data[i], point_precision)

        if velocity > 0:

            time = str(round(time, point_precision))
            height = str(round(h_data[i], point_precision))
            velocity = str(velocity)

            export_lines.append(time + ' ' + height + ' ' + velocity + '\n')


    # Open file for writing
    export_file = open(file_name, 'w')

    # Write the number of points following
    n_data = int(len(export_lines))

    export_file.write(str(n_data)+'\n\n')

    # Write lines to file
    for line in export_lines:
        export_file.write(line)

    export_file.close()

def inflectionFinder(func2ndDerive, args1, funcExtend2ndDerive, args2, max_value, sample_points=100):
    """ Find the inflection point of a given function.

    epsilon: the difference between the window to look for sign changes in the second derivative"""

    domain = np.linspace(0, max_value, sample_points)

    step = max_value / sample_points

    # Look for sign change in the function's second derivative
    for i in domain:
        #print func2ndDerive(i, *args1) - funcExtend2ndDerive(i, *args2)
        if np.sign(func2ndDerive(i, *args1) - funcExtend2ndDerive(i, *args2)) != np.sign(func2ndDerive(i + step, *args1) - funcExtend2ndDerive(i + step, *args2)):
            # Return the mean value of the two points between which the change in the derivative sign has been detected
            return (2*i + step) / 2

    return max_value



def funcsIntersect(x, ycoeffs, y_extended):
    """ Find intersections of 2 exponential curves given by func and funcExtend adn returns the first intersection after the inflection point. """

    # Generate initial values for the intersection calculations (each initial value will converge to the closest intersection)
    # The goal here is to uniformly cover the whole domain to find all intersection points
    max_range = max(x)

    x0_range = []

    # Sample the time domain with uniformly distributed points
    for i in np.linspace(0, max_range, len(x)):
        x0_range.append(i)

    # Find all intersections closest to the given starting points in the time domain
    intersections = sorted([float(fsolve(lambda x: func(x, *ycoeffs) - funcExtend(x, *y_extended), x0)) for x0 in x0_range])

    # Find inflexion point
    inflection = inflectionFinder(func2ndDerive, ycoeffs, funcExtend2ndDerive, y_extended, max_range)

    # Find the next intersection after the inflection point
    for point in intersections:
        if point > inflection:
            return point

    # If it is not found, return the last intersection point
    return intersections[-1]


def fitData(t_data, y_data, sigma_data, sampled=True, step=0.2, velocity=False, int_point=None, coeff_name='x'):
    """ Fits the given data to the provided funtiones defined (func and funcExtend). 

    sampled: If True, it will return the sampled time domain with <step> spaced samples, if False, it will use the original t_data time points
    step: optional - used when sampled == True, defines the time spacing between each sample
    velocity: If False it returns the fit in the spatial space, if True it returns the fitted velocity
    int_point: Precalculated intersection point, default None
    coef_name: Name of the coeficient to be calculated (used for file saving)
    """

    ## Fit y_data

    # First fit with 7 parameters
    y_extended, pcov = curve_fit(funcExtend, xdata = t_data, ydata = y_data, sigma = sigma_data, p0=(1, 1, 1, 1, 1, 1))

    # Take the parameters for a better guess with 4 coeff. fit
    y_p0 = y_extended[:4]

    # x_coeffs contains curve coeficients, p0 is the inital guess for the coeficients
    ycoeffs, pcov = curve_fit(func, xdata = t_data, ydata = y_data, sigma = sigma_data, p0=y_p0)

    if sampled:
        t_data = np.arange(0, max(t_data), step)
        max_value = np.array([max(t_data)])
        t_data = np.concatenate((t_data, max_value))

    if extended_ending:

        # Find intersection points of the 4 parameter and 6 parameter curve
        print 'Best intersection point between the 4 and 6 parameter curve:'
        if not int_point:
            int_point = funcsIntersect(t_data, ycoeffs, y_extended)

        intersection = [int_point, func(int_point, *ycoeffs)]
        print intersection

        # Take the 1st part of the curve from the 4 parameter curve, and the 2nd part from the 6 parameter curve
        t1_data = []
        t2_data = []
        
        for point in t_data:
            if point <= int_point:
                t1_data.append(point)
            else:
                t2_data.append(point)

        t1_data = np.array(t1_data)
        t2_data = np.array(t2_data)

        # Calculate function value for each parameter curve

        if velocity:
            # Calculate velocity
            fitted_data = np.concatenate( (funcDerive(t1_data, *ycoeffs), funcExtendDerive(t2_data, *y_extended)) )
        else:
            # Calculate path
            fitted_data = np.concatenate( (func(t1_data, *ycoeffs), funcExtend(t2_data, *y_extended)) )

            # Save parameter files
            saveCoeffs(ycoeffs, coeff_name + '_4param_coeffs.txt')
            saveCoeffs(y_extended, coeff_name + '_6param_coeffs.txt', tx = int_point)

        t_data = np.concatenate( (t1_data, t2_data) )


    else:
        if velocity:
            fitted_data = funcDerive(t_data, *ycoeffs)
            #fitted_data = funcExtendDerive(t_data, *y_extended)
        else:
            fitted_data = func(t_data, *ycoeffs)
            saveCoeffs(ycoeffs, coeff_name + '_4param_coeffs.txt')

        intersection = [None, None]
        

    # Test plot
    #test_data = func2ndDerive(t_data, *ycoeffs) - funcExtend2ndDerive(t_data, *y_extended)
    #plt.scatter(t_data, test_data, s = 3, c = 'k', edgecolors='none')

    return ycoeffs, intersection, fitted_data, t_data



# Load data from a file
t_data, s_data, h_data, sigma_data = loadData(data_file)

s_coeffs, intersection, s_fit_points, t_points = fitData(t_data, s_data, sigma_data, sampled = time_domain_sample, step= time_sample_step, coeff_name = 's')

print 'Curve coefficients for s:', s_coeffs

# Save coefficients to a file
#saveCoeffs(s_coeffs, 's_coeffs.txt')

## Plot data

# Adjust calcaulted data points size, make it bigger when sampled
fitted_points_size = 3

if time_domain_sample:
    fitted_points_size *= 2

## Plot s_data
plt.subplot(3, 1, 1)
plt.grid()
plt.title('Fireball trajectory')

# Plot input data points (blue)
real_data = plt.scatter(t_data, s_data, s = 3, c = 'b', edgecolors='none')
plt.ylabel('Realtive path (km)')

# Plot fitted function points (red)
fitted_data = plt.scatter(t_points, s_fit_points, s = fitted_points_size, c = 'r', edgecolors='none')

# Plot the intersection point
if intersection:
    plt.plot([intersection[0]], [intersection[1]], 'ko', ms = 5, alpha = 0.5)

#Plot the legend
plt.legend((real_data, fitted_data),
           ('Real data', 'Fitted data'),
           scatterpoints=1,
           loc='upper left',
           fontsize=10)


## Plot h_data
plt.subplot(3, 1, 2)
plt.grid()

## Fit h_data

h_coeffs, intersection, h_fit_points, t_points = fitData(t_data, h_data, sigma_data, sampled = time_domain_sample, step= time_sample_step, int_point = intersection[0], coeff_name = 'h')

print 'Curve coefficients for h:', h_coeffs

# Save coefficients to a file
#saveCoeffs(h_coeffs, 'h_coeffs.txt')

# Plot input data points (blue)
real_data = plt.scatter(t_data, h_data, s = 3, c = 'b', edgecolors='none')

# Plot fitted function points (red)
fitted_data = plt.scatter(t_points, h_fit_points, s = fitted_points_size, c = 'r', edgecolors='none')
plt.ylabel('Height (km)')

# Plot the intersection point
if intersection:
    plt.plot([intersection[0]], [intersection[1]], 'ko', ms = 5, alpha = 0.5)


## Plot velocity
plt.subplot(3, 1, 3)
plt.grid()

# Calculate velocity from the fitted curve
s_coeffs, intersection, v_data, t_points = fitData(t_data, s_data, sigma_data, velocity = True, sampled = time_domain_sample, step= time_sample_step, int_point = intersection[0])
# Plot fitted function points (red)
velocity_data = plt.scatter(t_points, v_data, s = fitted_points_size, c = 'g', edgecolors='none')
plt.ylabel('Velocity (km/s)')

#Plot the legend
plt.legend((velocity_data, ),
           ('Velocity (derived from path fit)', ),
           scatterpoints=1,
           loc='lower left',
           fontsize=10)


plt.xlabel('Time (s)')

# Export fitted data to a file
exportDataMaria(t_points, h_fit_points, v_data)

s_coeffs, intersection, v_data, t_points = fitData(t_data, s_data, sigma_data, velocity = True, sampled = False, int_point = intersection[0])

# Export raw heights and original time domain velocities to a file
exportDataMaria(t_data, h_data, v_data, file_name = "Alex_raw.txt")

plt.show()