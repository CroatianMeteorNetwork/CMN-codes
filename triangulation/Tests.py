""" Tests for the MeteorApplyAstrometry module. """

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

import numpy as np
import matplotlib.pyplot as plt

from MeteorApplyAstrometry import *

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
    JD_data, RA_data, dec_data = altAz2RADec(lat, lon, UT_corr, time_data, azimuth_data, altitude_data)

    print 'Time input: '
    print time_data
    print 'JD output:'
    print JD_data
    print 'JD referent data:'
    print """[ 2455597.47270073,  2455597.47270119,  2455597.47270166,
        2455597.47270814,  2455597.47270855,  2455597.47270892,
        2455597.47270953,  2455597.47271   ,  2455597.47271045,
        2455597.47271093,  2455597.47271185,  2455597.4727123 ,
        2455597.47271277,  2455597.47271323,  2455597.47271369,
        2455597.47271417,  2455597.47271462,  2455597.47271509,
        2455597.47271554,  2455597.47271602,  2455597.47271647,
        2455597.47271693,  2455597.4727174 ,  2455597.47271786]"""

    print '\nAzimuth input:'
    print azimuth_data
    print 'Altitude input:'
    print altitude_data
    print 'RA output:'
    print RA_data
    print 'RA referent data:'
    print """[ 169.73479836,  170.02226645,  170.32665095,  175.12114892,
        175.47943184,  175.83420354,  176.21175928,  176.54995668,
        176.94707024,  177.36689942,  178.23065134,  178.65285034,
        179.07584626,  179.48063408,  179.9264849 ,  180.39224408,
        180.88016793,  181.34760373,  181.73427589,  182.2230387 ,
        182.67309841,  183.12369291,  183.63601603,  184.17000324]"""
    print 'Dec output:'
    print dec_data
    print 'Dec referent data:'
    print """[ 38.64211095,  38.7115295 ,  38.79935026,  39.72668535,
        39.7781751 ,  39.86000181,  39.92809123,  39.98981577,
        40.07431817,  40.14466208,  40.2685085 ,  40.33512527,
        40.40051092,  40.44669495,  40.49618258,  40.56214409,
        40.61296624,  40.67582004,  40.72932596,  40.80698864,
        40.84789279,  40.88736589,  40.94618865,  40.98904247]"""


def testCalculateMagnitudes():
    """ Test the calculateMagnitudes function. """

    # Init platepar parameters
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

    # Init input data
    level_data = [62, 62, 62, 5200, 6780, 7572, 9154, 10341, 9553, 9950, 13907, 11536, 11934, 14705, 15894, 
    16690, 17880, 19470, 20664, 21467, 27022, 27821, 27039, 31413]


    ra_beg = 169.73480
    ra_end = 184.17000
    dec_beg = 38.64211
    dec_end = 40.98904

    duration = (2455597.4727178589 - 2455597.4727007290) * 86400

    # Run the function
    magnitude_data = calculateMagnitudes(level_data, ra_beg, ra_end, dec_beg, dec_end, duration, mag_0, 
        mag_lev, w_pix)

    print 'Input levles:'
    print level_data
    print 'ra_beg, ra_end:', ra_beg, ra_end
    print 'dec_beg, dec_end:', dec_beg, dec_end
    print 'duration:', duration
    print 'mag_0, mag_lev:', mag_0, mag_lev
    print 'w_pix:', w_pix

    print 'Output:'
    print magnitude_data
    print 'Referent output data:'
    print """[  3.48510742   3.48510742   3.48510742  -9.82006687 -12.12459388
 -13.08421211 -14.73221816 -15.79125076 -15.10279555 -15.45646161
 -18.36466909 -16.74110495 -17.03572067 -18.84930058 -19.52466417
 -19.94912673 -20.54735029 -21.28731903 -21.80428786 -22.13542713
 -24.13434979 -24.38745472 -24.13981252 -25.44218829]"""


def testXY2CorrectedRADec():
    """ Test the XY2CorrectedRADec function. """

     # Init platepar parameters
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
    time_data = np.array([[2011,02,05,00,20,41,343], [2011,02,05,00,20,41,383], [2011,02,05,00,20,41,423], 
        [2011,02,05,00,20,41,983], [2011,02,05,00,20,42,023], [2011,02,05,00,20,42,063], 
        [2011,02,05,00,20,42,103], [2011,02,05,00,20,42,144], [2011,02,05,00,20,42,183], 
        [2011,02,05,00,20,42,224], [2011,02,05,00,20,42,304], [2011,02,05,00,20,42,343], 
        [2011,02,05,00,20,42,383], [2011,02,05,00,20,42,423], [2011,02,05,00,20,42,463], 
        [2011,02,05,00,20,42,504], [2011,02,05,00,20,42,543], [2011,02,05,00,20,42,584], 
        [2011,02,05,00,20,42,623], [2011,02,05,00,20,42,664], [2011,02,05,00,20,42,703], 
        [2011,02,05,00,20,42,743], [2011,02,05,00,20,42,783], [2011,02,05,00,20,42,823]])

    X_data = np.array([329.000, 327.000, 324.750, 293.000, 290.750, 288.250, 285.750, 283.500, 280.750, 
        278.000, 272.500, 269.750, 267.000, 264.500, 261.750, 258.750, 255.750, 252.750, 250.250, 247.000, 
        244.250, 241.500, 238.250, 235.000])

    Y_data = np.array([122.250, 124.000, 125.750, 155.250, 157.500, 159.500, 161.750, 163.750, 166.000, 
        168.500, 173.750, 176.250, 178.750, 181.250, 184.000, 186.750, 189.750, 192.500, 194.750, 197.500, 
        200.250, 203.000, 206.000, 209.250])

    level_data = np.array([40, 40, 40, 3355, 4375, 4885, 5905, 6670, 6160, 6415, 8965, 7435, 7690, 9475, 
        10240, 10750, 11515, 12535, 13300, 13810, 17380, 17890, 17380, 20185])

    UT_corr = 1

    JD_data, RA_data, dec_data, magnitude_data = XY2CorrectedRADec(time_data, X_data, Y_data, level_data, 
        UT_corr, lat, lon, Ho, X_res, Y_res, RA_d, dec_d, rot_param, F_scale, w_pix, mag_0, mag_lev, x_poly, 
        y_poly)

    print 'Time data input:'
    print time_data
    print 'X data input:'
    print X_data
    print 'Y data input:'
    print Y_data
    print 'level data input:'
    print level_data
    print 'UT correction: ', UT_corr
    print 'JD data output:'
    print JD_data
    print 'JD data referent output:'
    print """[ 2455597.47270073  2455597.47270119  2455597.47270166  2455597.47270814
  2455597.47270855  2455597.47270892  2455597.47270953  2455597.47271
  2455597.47271045  2455597.47271093  2455597.47271185  2455597.4727123
  2455597.47271277  2455597.47271323  2455597.47271369  2455597.47271417
  2455597.47271462  2455597.47271509  2455597.47271554  2455597.47271602
  2455597.47271647  2455597.47271693  2455597.4727174   2455597.47271786]"""
    print 'RA output:'
    print RA_data
    print 'RA referent output:'
    print """[ 169.73480048  170.02226255  170.32665179  175.12115023  175.47942985
  175.83420848  176.21176637  176.54996223  176.94707542  177.36689701
  178.2306537   178.65285084  179.07584546  179.48062569  179.9264902
  180.39224393  180.88016857  181.34760665  181.73428144  182.22304536
  182.67309335  183.12369621  183.63600683  184.16999768]"""
    print 'Dec output:'
    print dec_data
    print 'Dec referent output:'
    print """[ 38.64210862  38.7115315   38.79935354  39.72668748  39.77817383
  39.8600033   39.92808595  39.98981695  40.07431807  40.14466606
  40.26850165  40.33512312  40.40051285  40.44669711  40.49618477
  40.56214126  40.61296956  40.67582588  40.7293291   40.80698699
  40.84789055  40.88736556  40.94619039  40.98904837]"""
    print 'Magnitude output:'
    print magnitude_data
    print 'Magnitude data output:'
    print """[  3.48389498   3.48400735   3.48392289  -9.81942599 -12.12449714
 -13.08419594 -14.73210999 -15.79118523 -15.10256239 -15.45604315
 -18.36464263 -16.74086599 -17.03552977 -18.84920382 -19.52444972
 -19.94891233 -20.54729378 -21.28715099 -21.80423445 -22.13537122
 -24.13430286 -24.38748251 -24.13994972 -25.44227085]"""



if __name__ == '__main__':

    # Run tests
    print 'Field correction test:'
    testApplyFieldCorrection()
    print 'XY2altAZ test:'
    testXY2altAz()
    print 'altAz2RADec test:'
    testaltAz2RADec()
    print 'Magnitude test:'
    testCalculateMagnitudes()
    print 'XY2RADec test:'
    testXY2CorrectedRADec()