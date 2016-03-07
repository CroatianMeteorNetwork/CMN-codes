"""
A module for triangulating a point on the meteor track.

See the function "triangulate" for more details.

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


import math
from datetime import datetime, timedelta

from MeteorTools import (EARTH_CONSTANTS, floatArguments, date2JD, equatorialCoordPrecession, geo2Cartesian, 
    stellar2Vector, cartesian2Geographical)


### CONSTANTS ###

# Initialize Earth shape constants object
EARTH = EARTH_CONSTANTS()

#################


@floatArguments
def findClosestPoints(Px, Py, Pz, Qx, Qy, Qz, ux, uy, uz, vx, vy, vz):
    """ Finds coordinates of closest points on lines represented by vectors u and v (on positions P and Q).

    @param Px: [float] X coordinate of the 1st observer
    @param Py: [float] Y coordinate of the 1st observer
    @param Pz: [float] Z coordinate of the 1st observer
    @param Qx: [float] X coordinate of the 2nd observer
    @param Qy: [float] Y coordinate of the 2nd observer
    @param Qz: [float] Z coordinate of the 2nd observer
    @param ux: [float] 1st observer's direction vector, X component
    @param uy: [float] 1st observer's direction vector, Y component
    @param uz: [float] 1st observer's direction vector, Z component
    @param vx: [float] 2nd observer's direction vector, X component
    @param vy: [float] 2nd observer's direction vector, Y component
    @param vz: [float] 2nd observer's direction vector, Z component

    @return (Sx, Sy, Sz, Tx, Ty, Tz, d): [tuple of floats]
        Sx: X coordinate of the closest point on the 1st observer's line of sight
        Sy: Y coordinate of the closest point on the 1st observer's line of sight
        Sz: Z coordinate of the closest point on the 1st observer's line of sight
        Tx: X coordinate of the closest point on the 2nd observer's line of sight
        Ty: Y coordinate of the closest point on the 2nd observer's line of sight
        Tz: Z coordinate of the closest point on the 2nd observer's line of sight
        d: distance in meters from points S and T
    """

    # Calculate differences of coordinates
    wx = Px - Qx
    wy = Py - Qy
    wz = Pz - Qz

    # Calculate coeficients for the equation
    a = ux**2 + uy**2 + uz**2
    b = ux*vx + uy*vy + uz*vz
    c = vx**2 + vy**2 + vz**2
    d = ux*wx + uy*wy + uz*wz
    e = vx*wx + vy*wy + vz*wz

    # Calculate sc and tc parameters
    sc = (b*e - c*d) / (a*c - b**2)
    tc = (a*e - b*d) / (a*c - b**2)

    # Calculate coordinates of closest points from both lines
    Sx = Px + ux*sc
    Sy = Py + uy*sc
    Sz = Pz + uz*sc

    Tx = Qx + vx*tc
    Ty = Qy + vy*tc
    Tz = Qz + vz*tc

    # Calculate the distance from two poaints
    dx = Sx - Tx
    dy = Sy - Ty
    dz = Sz - Tz

    d = math.sqrt(dx**2 + dy**2 + dz**2)

    return Sx, Sy, Sz, Tx, Ty, Tz, d


def triangulate(julian_date, lat1, lon1, h1, ra1, dec1, lat2, lon2, h2, ra2, dec2, epoch_correction=True):
    """ Triangulate a meteor detection point between 2 stations given the station's position and stellar 
        coordinates of the detections.

    @param julian_date: [float] decimal julian date, epoch J2000.0
    @param lat1: [float] latitude of the 1st observer in degrees
    @param lon1: [float] longitde of the 1st observer in degress
    @param h1: [int or float] elevation of the 1st observer in meters
    @param ra1: [float] right ascension of the line of sight from the 1st observer in degrees
    @param dec1: [float] declination of the line of sight from the 1st observer in degrees
    @param lat2: [float] latitude of the 2nd observer in degrees
    @param lon2: [float] longitde of the 2nd observer in degress
    @param h2: [int or float] elevation of the 2nd observer in meters
    @param ra2: [float] right ascension of the line of sight from the 2nd observer in degrees
    @param dec2: [float] declination of the line of sight from the 2nd observer in degrees
    @param epoch_correction: [bool] correct RA and Dec for precession from epoch J2000.0 to the current epoch

    @return (lon_avg, lat_avg, elevation, est_error): [tuple of floats]
        lon_avg: longitude of the midpoint between the 2 estimated points on the lines of sight (degress)
        lat_avg: latitude of the midpoint between the 2 estimated points on the lines of sight (degress)
        elevation: elevation of the point (meters)
        est_error: estimated error of the solution (meters)
    

    """

    # Presess RA and Dec to J2000.0 epoch
    if epoch_correction:
        ra1, dec1 = equatorialCoordPrecession(date2JD(2000, 1, 1, 12, 0, 0), julian_date, ra1, dec1)
        ra2, dec2 = equatorialCoordPrecession(date2JD(2000, 1, 1, 12, 0, 0), julian_date, ra2, dec2)


    # Convert geographical position to Cartesian coordinates for both stations
    X1, Y1, Z1 = geo2Cartesian(lat1, lon1, h1, julian_date)
    X2, Y2, Z2 = geo2Cartesian(lat2, lon2, h2, julian_date)

    # Convert right ascension and declination to a vector in Cartesian space
    xt1, yt1, zt1 = stellar2Vector(ra1, dec1)
    xt2, yt2, zt2 = stellar2Vector(ra2, dec2)

    # Find closest points on intersecting lines for both stations
    Xi1, Yi1, Zi1, Xi2, Yi2, Zi2, d = findClosestPoints(X1, Y1, Z1, X2, Y2, Z2, xt1, yt1, zt1, xt2, yt2, zt2)

    # Calculate average coordinates
    Xi_avg, Yi_avg, Zi_avg = (Xi1+Xi2)/2, (Yi1+Yi2)/2, (Zi1+Zi2)/2

    # Get point in geographical coordinates
    lon_avg, lat_avg = cartesian2Geographical(julian_date, lon1, Xi_avg, Yi_avg, Zi_avg)

    # Get height of point from Earth centre
    R_point = math.sqrt(EARTH.POLAR_RADIUS**2 + (EARTH.SQR_DIFF/((EARTH.RATIO * 
        math.tan(math.radians(lat_avg))) * (EARTH.RATIO * math.tan(math.radians(lat_avg))) + 1)))

    # Get points' sea level elevation
    elevation = math.sqrt(Xi_avg**2 + Yi_avg**2 + Zi_avg**2) - R_point

    # Angle of intersection of two vectors (radians)
    angle = math.acos((xt1*xt2 + yt1*yt2 + zt1*zt2) / ((xt1**2 + yt1**2 + zt1**2) * (xt2**2 + yt2**2 + 
        zt2**2)))

    # Estimated error
    est_error = d / 2 / math.sin(angle)


    return lon_avg, lat_avg, elevation, est_error



if __name__ == '__main__':

    ### INPUT PARAMETERS ###
    # year, month, day, hours, minutes, seconds
    julian_date = date2JD(2011, 2, 4, 23, 20, 41)

    # Station 1
    lon1 = 18.418047 # deg
    lat1 = 45.682317 # deg
    h1 = 91 # m

    ra1 = 70.593 # deg
    dec1 = 22.939 # deg

    # Station 2
    lon2 = 15.964008 # deg
    lat2 = 45.807056 # deg
    h2 = 117 # m

    ra2 = 170.327 # deg
    dec2 = 38.799 # deg

    ######################

    # Triangulate!
    point_params = triangulate(julian_date, lat1, lon1, h1, ra1, dec1, lat2, lon2, h2, ra2, dec2)

    # Print results
    print 'Longitude: ', point_params[0], ' deg'
    print 'Latitude: ', point_params[1], ' deg'
    print 'Elevation: ', point_params[2], ' m'
    print 'Estimation error +/-: ', point_params[3], ' m'

