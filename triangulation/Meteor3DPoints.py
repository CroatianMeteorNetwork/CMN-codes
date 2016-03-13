""" Pairs two FF files and generates 3D point cloud of triangulated points. """

# The MIT License

# Copyright (c) 2016 Denis Vida

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import math
import datetime
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from FF_bin_suite import readFF
from ParseCMNformat import parsePlatepar
from MeteorApplyAstrometry import applyFieldCorrection, XY2altAz, altAz2RADec
from MeteorTriangulation import triangulate


def thresholdFF(ff, k1):
    """ Threshold the FF bin image. """

    return (ff.maxpixel >= (ff.avepixel + float(k1)*ff.stdpixel))*ff.maxpixel



def generateTimeData(ff_path, ff, x_inds, y_inds, dT=0, fps=25):
    """ Generate a timestamp for each thresholded pixel from the FF file. """

    def formatDate(t):
        """ Converts datetime object to a list of values. """

        return np.array([t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond/1000])

    # Vectorize the formatDate function
    formatDate = np.vectorize(formatDate, otypes=[np.ndarray])

    # Extract time from the filename
    ff_name = ff_path.split(os.sep)[-1]
    ff_name = ff_name.split("_")
    
    year = int(ff_name[1][0:4])
    month = int(ff_name[1][4:6])
    date = int(ff_name[1][6:8])
    hour = int(ff_name[2][0:2])
    minute = int(ff_name[2][2:4])
    second = int(ff_name[2][4:6])
    ms = int(ff_name[3])

    # Convert time data to datetime object
    datetime_obj = datetime.datetime(year, month, date, hour, minute, second, ms*1000)

    # Shift the time if necessary
    if dT:
        datetime_obj += datetime.timedelta(seconds=dT)

    # Calculate one frame duration
    frame_delta = datetime.timedelta(seconds=1/float(fps))


    # Extract frame number of each given pixel
    frames = ff.maxframe[x_inds, y_inds]

    # Convert frame numbers to datetime objects of proper time
    time_data = datetime_obj + frames * frame_delta

    # Convert datetime objects to numpy arrays
    time_data = formatDate(time_data)

    return time_data



def generate3DPointCloud(platepar_name1, platepar_name2, FF_name1, FF_name2, UT_corr1, UT_corr2, k1, max_dT, dT):
    """ Pairs each point from one FF file to another. """

    # Read platepar files to import station parameters
    pp1 = parsePlatepar(platepar_name1)
    pp2 = parsePlatepar(platepar_name2)

    # Read FF image files
    FF1 = readFF(FF_name1)
    FF2 = readFF(FF_name2)

    # Threshold FF files
    thresh1 = thresholdFF(FF1, k1)
    thresh2 = thresholdFF(FF2, k1)

    plt.imshow(thresh1, cmap='gray')
    plt.show()
    plt.clf()

    plt.imshow(thresh2, cmap='gray')
    plt.show()
    plt.clf()
    plt.close()

    # Extract indices of the threshold passers
    x_inds1, y_inds1 = np.where(thresh1 > 0)
    x_inds2, y_inds2 = np.where(thresh2 > 0)

    print 'Converting image1 data...'
    ### IMAGE 1 PROCESSING ###

    # Generate time data from file name and frames
    time_data1 = generateTimeData(FF_name1, FF1, x_inds1, y_inds1, dT)

    # Generate dummy levels
    level_data = np.zeros_like(x_inds1)

    # Apply field correction
    x_corrected, y_corrected, _ = applyFieldCorrection(pp1.x_poly, pp1.y_poly, pp1.X_res, pp1.Y_res, 
        pp1.F_scale, x_inds1, y_inds1, level_data)

    # Convert XY image coordinates to azimuth and altitude
    az_data, alt_data = XY2altAz(pp1.lat, pp1.lon, pp1.RA_d, pp1.dec_d, pp1.Ho, pp1.rot_param, x_corrected, 
        y_corrected)

    # Convert azimuth and altitude data to right ascension and declination
    JD_data1, RA_data1, dec_data1 = altAz2RADec(pp1.lat, pp1.lon, UT_corr1, time_data1, az_data, alt_data)

    ##########################

    print 'Converting image2 data...'
    ### IMAGE 2 PROCESSING ###

    # Generate time data from file name and frames
    time_data2 = generateTimeData(FF_name2, FF2, x_inds2, y_inds2)

    # Generate dummy levels
    level_data = np.zeros_like(x_inds2)

    # Apply field correction
    x_corrected, y_corrected, _ = applyFieldCorrection(pp2.x_poly, pp2.y_poly, pp2.X_res, pp2.Y_res, 
        pp2.F_scale, x_inds2, y_inds2, level_data)

    # Convert XY image coordinates to azimuth and altitude
    az_data, alt_data = XY2altAz(pp2.lat, pp2.lon, pp2.RA_d, pp2.dec_d, pp2.Ho, pp2.rot_param, x_corrected, 
        y_corrected)

    # Convert azimuth and altitude data to right ascension and declination
    JD_data2, RA_data2, dec_data2 = altAz2RADec(pp2.lat, pp2.lon, UT_corr2, time_data2, az_data, alt_data)

    ##########################

    print 'Pairing pixels...'

    print RA_data1
    print RA_data2

    # Pair each point from both arrays with another
    triangulated_points = []
    for JD1, ra1, dec1 in np.vstack((JD_data1, RA_data1, dec_data1)).T:

        for JD2, ra2, dec2 in np.vstack((JD_data2, RA_data2, dec_data2)).T:

            # Limit time difference
            if abs(JD2 - JD1) < (max_dT)/86400.0:

                # Triangulate all points with each other
                triangulated_points.append(triangulate(JD1, pp1.lat, pp1.lon, pp1.elev, ra1, dec1, pp2.lat, 
                    pp2.lon, pp2.elev, ra2, dec2))


    print 'Pairing done!'

    # Convert results to numpy array
    triangulated_points = np.array(triangulated_points)

    # Filter by estimated error
    max_error = 500 # meters
    error_limit = triangulated_points[:,3]
    error_good_indices = np.where(error_limit < max_error)

    # Filter by height
    max_height = 100 * 1000
    min_height = 40 * 1000

    height_limit = triangulated_points[:,2]
    height_good_indices = np.where((height_limit > min_height) & (height_limit < max_height))

    # Find common indices
    good_indices = np.intersect1d(error_good_indices, height_good_indices)

    print 'Number of points:', len(good_indices)

    xs = triangulated_points[:,0][good_indices]
    ys = triangulated_points[:,1][good_indices]
    zs = triangulated_points[:,2][good_indices]

    # Show triangulated points in 3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(xs, ys, zs, c='b', marker='o')

    ax.set_xlabel('Lat')
    ax.set_ylabel('Lon')
    ax.set_zlabel('h')

    plt.show()



    





if __name__ == '__main__':

    # Thresholding parameter
    k1 = 4.0

    # Known time difference between stations (first station lag, i.e. station1_time - station2_time)
    dT = 0.19

    # Max time difference between stations in seconds for point pairing
    max_dT = 0.1

    # Platepare files
    platepar_name1 = 'PUA/PUA.cal'
    platepar_name2 = 'HUM/HUM.cal'

    # FF file names
    FF_name1 = 'PUA/FF451_20151212_183245_460_0234496.bin'
    FF_name2 = 'HUM/FF475_20151212_183245_285_0237824.bin'

    # Get triangulated points
    print generate3DPointCloud(platepar_name1, platepar_name2, FF_name1, FF_name2, 0, 0, k1, max_dT, dT)