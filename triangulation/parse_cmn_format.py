""" This module contains functions for parsing CMN format data.
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

import numpy as np

from meteor_triangulation import date2JD

class stationData(object):
    """ Holds information about one meteor station (location) and observed points. """

    def __init__(self, file_name):
        self.file_name = file_name
        self.station_code = ''
        self.lon = 0
        self.lat = 0
        self.h = 0
        self.points = []

    def __str__(self):
        return 'Station: ' + self.station_code + ' data points: ' + str(len(self.points))


def parseInf(file_name):
    """ Parse information from an INF file to a stationData object. """

    station_data_obj = stationData(file_name)

    with open(file_name) as f:
        for line in f.readlines()[2:]:
            
            line = line.split()

            if 'Station_Code' in line[0]:
                station_data_obj.station_code = line[1]

            elif 'Long' in line[0]:
                station_data_obj.lon = float(line[1])

            elif 'Lati' in line[0]:
                station_data_obj.lat = float(line[1])

            elif 'Height' in line[0]:
                station_data_obj.h = int(line[1])

            else:
                station_data_obj.points.append(map(float, line))


    return station_data_obj


def parsePlatepar(file_name):
    """ Load calibration parameters from a platepar file. 

    """

    def parse(f):
        """ Read next line, split the line and convert parameters to float.

        @param f: [file handle] file we want to read

        @return (a1, a2, ...): [tuple of floats] parsed data from the line
         """

        return map(float, f.readline().split())


    with open(file_name) as f:

        # Parse latitude, longitude, elevation
        lat, lon, elev = parse(f)

        # Parse date and time as int
        D, M, Y, h, m, s = map(int, f.readline().split())

        # Convert time to JD
        JD = date2JD(Y, M, D, h, m, s)

        # Calculate the referent hour angle
        T=(JD - 2451545.0)/36525.0
        Ho = (280.46061837 + 360.98564736629*(JD - 2451545.0) + 0.000387933*T**2 - T**3/38710000.0) % 360

        # Parse camera parameters
        X_res, Y_res, focal_length = parse(f)

        # Parse the right ascension of the image centre
        RA_d, RA_H, RA_M, RA_S = parse(f)

        # Parse the declination of the image centre
        dec_d, dec_D, dec_M, dec_S = parse(f)

        # Parse the rotation parameter
        rot_param = parse(f)[0]

        # Parse the sum of image scales per each image axis (arcsec per px)
        F_scale = parse(f)[0]
        w_pix = 50*F_scale/3600
        F_scale = 3600/F_scale

        # Load magnitude slope parameters
        mag_0, mag_lev = parse(f)

        # Load X axis polynomial parameters
        x_poly = np.zeros(shape=(12,), dtype=np.float64)
        for i in range(12):
            x_poly[i] = parse(f)[0]

        # Load Y axis polynomial parameters
        y_poly = np.zeros(shape=(12,), dtype=np.float64)
        for i in range(12):
            y_poly[i] = parse(f)[0]

        # Read station code
        station_code = f.readline().replace('\r', '').replace('\n', '')


    return (lat, lon, elev, JD, Ho, X_res, Y_res, RA_d, dec_d, rot_param, F_scale, w_pix, mag_0, mag_lev, 
        x_poly, y_poly, station_code)

    # print lat, lon, elev
    # print D, M, Y, h, m, s, JD, Ho
    # print X_res, Y_res, focal_length
    # print RA_d, RA_H, RA_M, RA_S
    # print dec_d, dec_D, dec_M, dec_S
    # print rot_param
    # print F_scale, w_pix
    # print mag_0, mag_lev
    # print x_poly
    # print y_poly
    # print station_code