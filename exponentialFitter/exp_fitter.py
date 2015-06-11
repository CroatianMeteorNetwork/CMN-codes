from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np

def func(x, a, b, c, d):
    """ Define the function for fitting. """
    
    return a + b*x + c* np.exp(d*x)

def loadData(file_name):
    """ Loads input data from a given file into numpy arrays. Only First two columns are loaded. 
    The third column is optional and it contains data point weights. """

    x_data = []
    y_data = []
    sigma_data = []

    for line in open(file_name).readlines():
        line = line.split()

        # Load data
        x_data.append(float(line[0]))
        y_data.append(float(line[1]))

        # Check for weight data
        if len(line)>2:
            sigma_data.append(float(line[2]))

    if sigma_data:
        sigma_data = np.array(sigma_data, dtype = np.float32)
    else:
        sigma_data = None

    x_data = np.array(x_data, dtype = np.float32)
    y_data = np.array(y_data, dtype = np.float32)

    return x_data, y_data, sigma_data

def saveCoeffs(coeff_list, file_name = 'exp_par.txt'):
    """ Saves coefficients to a file. """

    save_file = open(file_name, 'w')

    for i, coeff in enumerate(coeff_list):
        save_file.write('a' + str(i + 1) + ' = '+ str(coeff) + '\n')

    save_file.close()



# INPUT FILE NAME
data_file = 'input.txt'

# Load data from a file
x_data, y_data, sigma_data = loadData(data_file)

# popt contains curve coeficients, p0 is the inital guess for the coeficients
popt, pcov = curve_fit(func, xdata = x_data, ydata = y_data, sigma = sigma_data, p0=(1, 1, 1, 1))

print 'Curve coefficients:', popt

# Save coefficients to a file
saveCoeffs(popt)

# Plot input data points (blue)
real_data = plt.scatter(x_data, y_data, s = 3, c = 'b', edgecolors='none')


# Plot fitted function points (red)
fitted_data = plt.scatter(x_data, func(x_data, *popt), s = 3, c = 'r', edgecolors='none')

#Plot the legend
plt.legend((real_data, fitted_data),
           ('Real data', 'Fitted data'),
           scatterpoints=1,
           loc='lower right',
           fontsize=10)

plt.show()