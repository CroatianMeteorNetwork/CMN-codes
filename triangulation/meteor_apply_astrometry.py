""" This module contains procedures for applying astrometry and field corrections to meteor data.
"""

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


import sys
import math
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from meteor_triangulation import date2JD, triangulate
from parse_cmn_format import parseInf, parsePlatepar



def applyFieldCorrection(x_poly, y_poly, X_res, Y_res, F_scale, X_data, Y_data, level_data):
    """ Apply field correction and vignetting correction to all given image points. 

    @param x_poly: [ndarray] 1D numpy array of 12 elements containing X axis polynomial parameters
    @param y_poly: [ndarray] 1D numpy array of 12 elements containing Y axis polynomial parameters
    @param X_res: [int] camera X axis resolution (longer)
    @param Y_res: [int] camera Y axis resolution (shorter)
    @param F_scale: [float] sum of image scales per each image axis (arcsec per px)
    @param X_data: [ndarray] 1D float numpy array containing X component of the detection point
    @param Y_data: [ndarray] 1D float numpy array containing Y component of the detection point
    @param level_data: [ndarray] 1D int numpy array containing levels of detection points

    @return (X_corrected, Y_corrected, levels_corrected): [tuple of ndarrays]
        X_corrected: 1D numpy array containing distortion corrected X component
        Y_corrected: 1D numpy array containing distortion corrected Y component
        level_data: 1D numpy array containing vignetting corrected levels
    """

    # Scale the resolution to CIF
    X_scale = X_res/384.0
    Y_scale = Y_res/288.0

    # Initialize final values containers
    X_corrected = np.zeros_like(X_data)
    Y_corrected = np.zeros_like(Y_data)
    levels_corrected = np.zeros_like(level_data, dtype=np.float64)

    i = 0

    data_matrix = np.vstack((X_data, Y_data, level_data)).T

    # Go through all given data points
    for Xdet, Ydet, level in data_matrix:

        # Scale the point coordinates to CIF resolution
        Xdet = (Xdet - X_res/2)/X_scale
        Ydet = (Ydet - Y_res/2)/Y_scale

        # Apply vignetting correction
        if (np.sqrt((Xdet - 192)**2 + (Ydet - 192)**2) > 120):
            level = level * (1 + 0.00245*(np.sqrt((Xdet - 192)**2 + (Ydet - 192)**2) - 120))

        X_pix = (
            Xdet 
            + x_poly[0]
            + x_poly[1] * Xdet
            + x_poly[2] * Ydet
            + x_poly[3] * Xdet**2
            + x_poly[4] * Xdet * Ydet
            + x_poly[5] * Ydet**2
            + x_poly[6] * Xdet**3
            + x_poly[7] * Xdet**2 * Ydet
            + x_poly[8] * Xdet * Ydet**2
            + x_poly[9] * Ydet**3
            + x_poly[10] * Xdet * np.sqrt(Xdet**2 + Ydet**2)
            + x_poly[11] * Ydet * np.sqrt(Xdet**2 + Ydet**2))

        Y_pix = (
            Ydet
            + y_poly[0]
            + y_poly[1] * Xdet
            + y_poly[2] * Ydet
            + y_poly[3] * Xdet**2
            + y_poly[4] * Xdet * Ydet
            + y_poly[5] * Ydet**2
            + y_poly[6] * Xdet**3
            + y_poly[7] * Xdet**2 * Ydet
            + y_poly[8] * Xdet * Ydet**2
            + y_poly[9] * Ydet**3
            + y_poly[10] * Ydet * np.sqrt(Xdet**2 + Ydet**2)
            + y_poly[11] * Xdet * np.sqrt(Xdet**2 + Ydet**2))


        # Scale back image coordinates
        X_pix = X_pix/F_scale
        Y_pix = Y_pix/F_scale

        # Store values to final arrays
        X_corrected[i] = X_pix
        Y_corrected[i] = Y_pix
        levels_corrected[i] = level

        i += 1

    return X_corrected, Y_corrected, levels_corrected


def visualizeFieldDistortion(x_poly, y_poly, X_res, Y_res, F_scale):
    """ Plots colourcoded field distortion. 

    @param x_poly: [ndarray] 1D numpy array of 12 elements containing X axis polynomial parameters
    @param y_poly: [ndarray] 1D numpy array of 12 elements containing Y axis polynomial parameters
    @param X_res: [int] camera X axis resolution (longer)
    @param Y_res: [int] camera Y axis resolution (shorter)
    @param F_scale: [float] sum of image scales per each image axis (arcsec per px)

    @return None
    """

    # Generate dummy image data
    X_data = np.tile(np.arange(0, X_res, 1), Y_res)
    Y_data = np.repeat(np.arange(0, Y_res), X_res)
    level_data = np.zeros(shape=(X_res*Y_res, ))

    # Apply the field correction
    X_corrected, Y_corrected, _ = applyFieldCorrection(x_poly, y_poly, X_res, Y_res, F_scale, X_data, Y_data, 
        level_data)

    # Calculate the geometrical distance of the correction
    correction_image = np.sqrt(X_corrected**2 + Y_corrected**2).reshape(Y_res, X_res)

    plt.imshow(correction_image, cmap='magma')
    plt.colorbar(label='Deviation in pixels')
    plt.title('Image field correction')
    plt.xlabel('Image X axis')
    plt.ylabel('Image Y axis')
    plt.show()


def testApplyFieldCorrection():
    """ Runs a test on the applyFieldCorrection function. """

    # Init test parameters
    (lat, lon, elev, JD, Ho, X_res, Y_res, RA_d, dec_d, rot_param, F_scale, w_pix, mag_0, mag_lev, 
        x_poly, y_poly, station_code) = (15.964008, 45.807056, 117.0, 2455132.461539352, 22.586806698469445, 
        720.0, 576.0, 78.75769, 27.85434, 310.0927, 5.8622959385671765, 8.529081527777779, -3.3, 9.4, 
        np.array([ -9.27430484e-03,   7.26937270e-03,  -8.23922106e-04,
        -1.02128215e-05,   3.86212560e-05,   2.99215708e-06,
        -1.60423224e-06,  -4.53053310e-08,  -1.65161816e-06,
        -1.09382725e-07,   2.61955924e-04,   2.11749029e-05]), 
        np.array([  9.59968427e-04,   3.96941541e-05,  -1.30518321e-02,
        -1.53957317e-05,  -1.38525365e-05,   1.87625046e-05,
         1.74017263e-08,  -1.64448807e-06,   1.45675934e-08,
        -1.66418545e-06,   2.57264212e-04,  -8.33460581e-06]), 'ZGR')

    # Init test data
    X_data = np.array([329.000, 327.000, 324.750, 293.000, 290.750, 288.250, 285.750, 283.500, 280.750, 
        278.000, 272.500, 269.750, 267.000, 264.500, 261.750, 258.750, 255.750, 252.750, 250.250, 247.000, 
        244.250, 241.500, 238.250, 235.000])

    Y_data = np.array([122.250, 124.000, 125.750, 155.250, 157.500, 159.500, 161.750, 163.750, 166.000, 
        168.500, 173.750, 176.250, 178.750, 181.250, 184.000, 186.750, 189.750, 192.500, 194.750, 197.500, 
        200.250, 203.000, 206.000, 209.250])

    level_data = np.array([40, 40, 40, 3355, 4375, 4885, 5905, 6670, 6160, 6415, 8965, 7435, 7690, 9475, 
        10240, 10750, 11515, 12535, 13300, 13810, 17380, 17890, 17380, 20185])

    # Run field correction procedure
    X_out, Y_out, level_out = applyFieldCorrection(x_poly, y_poly, X_res, Y_res, F_scale, X_data, Y_data, 
        level_data)

    print '\nX axis'
    print '----------'
    print 'INPUT:'
    print X_data
    print 'RESULT:'
    print X_out
    print 'REFERENT DATA:'
    print """[ -2.86236856  -3.04719928  -3.25513469  -6.19185256  -6.40013596
  -6.63155357  -6.86302001  -7.07136487  -7.32602925  -7.58075282
  -8.09034617  -8.34519762  -8.60009297  -8.83187601  -9.08688199
  -9.3650976   -9.64339373  -9.92171485 -10.15368178 -10.45526309
 -10.71054663 -10.96586915 -11.26761911 -11.56945304]"""

    print '\nY axis'
    print '----------'
    print 'INPUT:'
    print Y_data
    print 'RESULT:'
    print Y_out
    print 'REFERENT DATA:'
    print """[-14.07207931 -13.92415181 -13.77621303 -11.27899968 -11.08838317
 -10.91902237 -10.72843635 -10.55902807 -10.36848012 -10.15670276
  -9.71190577  -9.50011594  -9.28832167  -9.0764732   -8.84343232
  -8.61043173  -8.35618391  -8.12315962  -7.93250136  -7.69949574
  -7.46637823  -7.2332423   -6.97893309  -6.70335372]"""

    print '\nLevels'
    print '----------'
    print 'INPUT:'
    print level_data
    print 'RESULT:'
    print level_out
    print 'REFERENT DATA:'
    print """[    62.05247359     62.04760815     62.05126483   5199.61633635
   6779.92448893   7571.9859048    9153.88599556  10340.92198561
   9552.74355892   9949.52065046  13906.95763161  11535.68263849
  11933.737716    14704.83619069  15893.60758785  16689.58803531
  17879.88367214  19469.62334056  20663.87292556  21466.86183819
  27021.85398382  27821.08899214  27039.42712868  31413.29860968]"""

    print 'Preparing field correction image...'

    # Show field distortion
    visualizeFieldDistortion(x_poly, y_poly, X_res, Y_res, F_scale)


def XY2altAz(lat, lon, RA_d, dec_d, Ho, rot_param, X_data, Y_data):
    """ Convert image coordinates (X, Y) to sky altitude and azimuth. 

    @param lat: [float] latitude of the observer in degrees
    @param lon: [float] longitde of the observer in degress
    @param RA_d: [float] right ascension of the image centre (degrees)
    @param dec_d: [float] declination of the image centre (degrees)
    @param Ho: [float] referent hour angle
    @param rot_param: [float] field rotation parameter (degrees)
    @param X_data: [ndarray] 1D numpy array containing distortion corrected X component
    @param Y_data: [ndarray] 1D numpy array containing distortion corrected Y component

    @return (azimuth_data, altitude_data): [tuple of ndarrays]
        azimuth_data: [ndarray] 1D numpy array containing the azimuth of each data point (degrees)
        altitude_data: [ndarray] 1D numyp array containing the altitude of each data point (degrees)


    """

    # Initialize final values containers
    az_data = np.zeros_like(X_data)
    alt_data = np.zeros_like(X_data)

    # Convert declination to radians
    dec_rad = math.radians(dec_d)

    # Precalculate some parameters
    sl = math.sin(math.radians(lon))
    cl = math.cos(math.radians(lon))

    i = 0
    data_matrix = np.vstack((X_data, Y_data)).T

    # Go through all given data points
    for X_pix, Y_pix in data_matrix:

        # Caulucate the needed parameters
        radius = math.radians(np.sqrt(X_pix**2 + Y_pix**2))
        theta = math.radians((90 - rot_param + math.degrees(math.atan2(Y_pix, X_pix))) % 360)

        sin_t = math.sin(dec_rad)*math.cos(radius) + math.cos(dec_rad)*math.sin(radius)*math.cos(theta)
        Dec0det = math.atan2(sin_t, math.sqrt(1 - sin_t**2))

        sin_t = math.sin(theta)*math.sin(radius)/math.cos(Dec0det)
        cos_t = (math.cos(radius) - math.sin(Dec0det)*math.sin(dec_rad))/(math.cos(Dec0det)*math.cos(dec_rad))
        RA0det = RA_d - math.degrees(math.atan2(sin_t, cos_t)) % 360

        h = math.radians(Ho + lat - RA0det)
        sh = math.sin(h)
        sd = math.sin(Dec0det)
        ch = math.cos(h)
        cd = math.cos(Dec0det)

        x = -ch*cd*sl + sd*cl
        y = -sh*cd
        z = ch*cd*cl + sd*sl

        r = math.sqrt(x**2 + y**2)

        # Calculate azimuth and altitude
        azimuth = math.degrees(math.atan2(y, x)) % 360
        altitude = math.degrees(math.atan2(z, r))

        # Save calculated values to an output array
        az_data[i] = azimuth
        alt_data[i] = altitude
        
        i += 1

    return az_data, alt_data
    

def testXY2altAz():
    """ Run a test for XY2altAz function. """

    # Init test parameters
    (lat, lon, elev, JD, Ho, X_res, Y_res, RA_d, dec_d, rot_param, F_scale, w_pix, mag_0, mag_lev, 
        x_poly, y_poly, station_code) = (15.964008, 45.807056, 117.0, 2455132.461539352, 22.586806698469445, 
        720.0, 576.0, 78.75769, 27.85434, 310.0927, 5.8622959385671765, 8.529081527777779, -3.3, 9.4, 
        np.array([ -9.27430484e-03,   7.26937270e-03,  -8.23922106e-04,
        -1.02128215e-05,   3.86212560e-05,   2.99215708e-06,
        -1.60423224e-06,  -4.53053310e-08,  -1.65161816e-06,
        -1.09382725e-07,   2.61955924e-04,   2.11749029e-05]), 
        np.array([  9.59968427e-04,   3.96941541e-05,  -1.30518321e-02,
        -1.53957317e-05,  -1.38525365e-05,   1.87625046e-05,
         1.74017263e-08,  -1.64448807e-06,   1.45675934e-08,
        -1.66418545e-06,   2.57264212e-04,  -8.33460581e-06]), 'ZGR')


    # Init test data
    X_data = np.array([-02.86237, -03.04720, -03.25513, -06.19185, -06.40014, -06.63155, -06.86302, -07.07136, 
        -07.32603, -07.58075, -08.09035, -08.34520, -08.60009, -08.83188, -09.08688, -09.36510, -09.64339, 
        -09.92171, -10.15368, -10.45526, -10.71055, -10.96587, -11.26762, -11.56945])
    Y_data = np.array([-14.07208, -13.92415, -13.77621, -11.27900, -11.08838, -10.91902, -10.72844, -10.55903, 
        -10.36848, -10.15670, -09.71191, -09.50012, -09.28832, -09.07647, -08.84343, -08.61043, -08.35618, 
        -08.12316, -07.93250, -07.69950, -07.46638, -07.23324, -06.97893, -06.70335])

    # Run the tested function
    azimuth_data, altitude_data = XY2altAz(lat, lon, RA_d, dec_d, Ho, rot_param, X_data, Y_data)

    print 'Azimuth input:'
    print X_data
    print 'Azimuth output:'
    print azimuth_data
    print 'Azimuth referent output:'
    print """[ 98.35602945  97.92081775  97.43250456  91.39096015  91.01584665
  90.58488236  90.17063391  89.80218321  89.35005501  88.91615115
  88.08123162  87.66852671  87.26249379  86.909805    86.52814773
  86.10695169  85.70518294  85.29826653  84.96229503  84.52362235
  84.17953969  83.84089844  83.4347725   83.04847062]
  """

    print 'Altitude input:'
    print Y_data
    print 'Altitude output:'
    print altitude_data
    print 'Altitude referent output:'
    print """[ 67.62510799  67.45932175  67.28989846  64.36948081  64.14162693
  63.92881562  63.69423641  63.48427957  63.24254606  62.9790113
  62.42803871  62.16117209  61.89324049  61.6302426   61.3400555
  61.04275667  60.72405819  60.42458204  60.17756662  59.86947967
  59.57373329  59.27722515  58.94591388  58.59350364]"""


def altAz2RADec(lat, lon, UT_corr, time_data, azimuth_data, altitude_data):
    """ Convert the azimuth and altitude in a given time and position on Earth to right ascension and 
        declination. 

    @param lat: [float] latitude of the observer in degrees
    @param lon: [float] longitde of the observer in degress
    @param UT_corr: [float] UT correction in hours (difference from local time to UT)
    @param time_data: [2D ndarray] numpy array containing time tuples of each data point (year, month, day, 
        hour, minute, second, millisecond)
    @param azimuth_data: [ndarray] 1D numpy array containing the azimuth of each data point (degrees)
    @param altitude_data: [ndarray] 1D numyp array containing the altitude of each data point (degrees)

    @return (JD_data, RA_data, dec_data): [tuple of ndarrays]
        JD_data: [ndarray] julian date of each data point
        RA_data: [ndarray] right ascension of each point
        dec_data: [ndarray] declination of each point
    """

    # Initialize final values containers
    JD_data = np.zeros_like(azimuth_data)
    RA_data = np.zeros_like(azimuth_data)
    dec_data = np.zeros_like(azimuth_data)

    # Precalculate some parameters
    sl = math.sin(math.radians(lon))
    cl = math.cos(math.radians(lon))

    i = 0
    data_matrix = np.vstack((azimuth_data, altitude_data)).T

    # Go through all given data points
    for azimuth, altitude in data_matrix:

        # Extract time
        Y, M, D, h, m, s, ms = time_data[i]

        # Convert altitude and azimuth to radians
        az_rad = math.radians(azimuth)
        alt_rad = math.radians(altitude)

        saz = math.sin(az_rad)
        salt = math.sin(alt_rad)
        caz = math.cos(az_rad)
        calt = math.cos(alt_rad)

        x = -saz*calt
        y = -caz*sl*calt + salt*cl
        HA = math.degrees(math.atan2(x,y))

        # Calculate the referent hour angle
        JD = date2JD(Y, M, D, h, m, s, ms, UT_corr=UT_corr)
        T=(JD - 2451545.0)/36525.0
        Ho = (280.46061837 + 360.98564736629*(JD - 2451545.0) + 0.000387933*T**2 - T**3/38710000.0) % 360

        RA = (Ho + lat - HA) % 360
        dec = math.degrees(math.asin(sl*salt + cl*calt*caz))

        print JD, RA, dec

        # Save calculated values to an output array
        JD_data[i] = JD
        RA_data[i] = RA
        dec_data[i] = dec

        i += 1

    return JD_data, RA_data, dec_data


def testaltAz2RADec():
    """ Test the altAz2RADec function. """

    # Init test parameters
    (lat, lon, elev, JD, Ho, X_res, Y_res, RA_d, dec_d, rot_param, F_scale, w_pix, mag_0, mag_lev, 
        x_poly, y_poly, station_code) = (15.964008, 45.807056, 117.0, 2455132.461539352, 22.586806698469445, 
        720.0, 576.0, 78.75769, 27.85434, 310.0927, 5.8622959385671765, 8.529081527777779, -3.3, 9.4, 
        np.array([ -9.27430484e-03,   7.26937270e-03,  -8.23922106e-04,
        -1.02128215e-05,   3.86212560e-05,   2.99215708e-06,
        -1.60423224e-06,  -4.53053310e-08,  -1.65161816e-06,
        -1.09382725e-07,   2.61955924e-04,   2.11749029e-05]), 
        np.array([  9.59968427e-04,   3.96941541e-05,  -1.30518321e-02,
        -1.53957317e-05,  -1.38525365e-05,   1.87625046e-05,
         1.74017263e-08,  -1.64448807e-06,   1.45675934e-08,
        -1.66418545e-06,   2.57264212e-04,  -8.33460581e-06]), 'ZGR')


    time_data = np.array([[2011,02,05,00,20,41,343], [2011,02,05,00,20,41,383], [2011,02,05,00,20,41,423], 
        [2011,02,05,00,20,41,983], [2011,02,05,00,20,42,023], [2011,02,05,00,20,42,063], 
        [2011,02,05,00,20,42,103], [2011,02,05,00,20,42,144], [2011,02,05,00,20,42,183], 
        [2011,02,05,00,20,42,224], [2011,02,05,00,20,42,304], [2011,02,05,00,20,42,343], 
        [2011,02,05,00,20,42,383], [2011,02,05,00,20,42,423], [2011,02,05,00,20,42,463], 
        [2011,02,05,00,20,42,504], [2011,02,05,00,20,42,543], [2011,02,05,00,20,42,584], 
        [2011,02,05,00,20,42,623], [2011,02,05,00,20,42,664], [2011,02,05,00,20,42,703], 
        [2011,02,05,00,20,42,743], [2011,02,05,00,20,42,783], [2011,02,05,00,20,42,823]])

    azimuth_data = np.array([98.35603, 97.92082, 97.43250, 91.39096, 91.01585, 90.58488, 90.17063, 89.80218, 
        89.35006, 88.91615, 88.08123, 87.66853, 87.26249, 86.90981, 86.52815, 86.10695, 85.70518, 85.29827, 
        84.96230, 84.52362, 84.17954, 83.84090, 83.43477, 83.04847])

    altitude_data = np.array([67.62511, 67.45932, 67.28990, 64.36948, 64.14163, 63.92882, 63.69424, 63.48428, 
        63.24255, 62.97901, 62.42804, 62.16117, 61.89324, 61.63024, 61.34006, 61.04276, 60.72406, 60.42458, 
        60.17757, 59.86948, 59.57373, 59.27723, 58.94591, 58.59350])

    UT_corr = 1 #hrs

    # Run the tested function
    print altAz2RADec(lat, lon, UT_corr, time_data, azimuth_data, altitude_data)


def findPointTimePairs(station_obj1, station_obj2, max_dt):
    """ Find points that are closest in time. 

    ...
    @param max_dt: [float] maximum time difference between point pairs (in seconds)
    """

    max_dt = float(max_dt)/60/60/24

    point_pairs = []

    min_index = 0
    for point1 in station_obj1.points:

        min_diff = abs(point1[0] - station_obj2.points[min_index][0])

        for k, point2 in enumerate(station_obj2.points):

            # Calculate time difference between points
            diff = abs(point1[0] - point2[0])

            if diff < min_diff:
                min_index = k
                min_diff = diff

        # Check if the difference in time is too large
        if min_diff < max_dt:
            # Add points to the list
            point_pairs.append([point1, station_obj2.points[min_index]])

            print point1, station_obj2.points[min_index]

    return point_pairs



if __name__ == '__main__':

    # # pp_name = 'KOP.cal'
    # pp_name = 'rgn_test/platepar_CMN2010.inf'

    # print parsePlatepar(pp_name)

    # # Load the data from the Platepar file
    # (lat, lon, elev, JD, Ho, X_res, Y_res, RA_d, dec_d, rot_param, F_scale, w_pix, mag_0, mag_lev, 
    #     x_poly, y_poly, station_code) = parsePlatepar(pp_name)

    

    # Run tests
    # testApplyFieldCorrection()
    # testXY2altAz()
    testaltAz2RADec()


    sys.exit()

    # Data files from 2 stations
    station1 = 'M_2011020405RIA0001.inf'
    station2 = 'M_2011020405ZGR0001.inf'

    # Parse station information
    station_obj1 = parseInf(station1)
    station_obj2 = parseInf(station2)

    print station_obj1

    point_pairs = findPointTimePairs(station_obj1, station_obj2, 2)

    triangulated_points = []

    # Run the triangulation procedure on paired points
    for pair in point_pairs:

        jd1, ra1, dec1, _ = pair[0]
        jd2, ra2, dec2, _ = pair[1]

        # Store triangulation results
        triangulated_points.append(triangulate(pair[0][0], station_obj1.lat, station_obj1.lon, station_obj1.h, 
            ra1, dec1, station_obj2.lat, station_obj2.lon, station_obj2.h, ra2, dec2))

    print triangulated_points

    triangulated_points = np.array(triangulated_points)

    # Limit error
    error_limit = triangulated_points[:,3]
    good_indices = np.where(error_limit < 1000)

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