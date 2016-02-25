"""
A module for triangulating a point in the meteor track.

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

### CONSTANTS ###

# Define Julian epoch
JULIAN_EPOCH = datetime(2000, 1, 1, 12) # noon (the epoch name is unrelated)
J2000_JD = timedelta(2451545) # julian epoch in julian dates

# Earth elipsoid parameters in meters (source: IERS 2003)
EARTH_EQUATORIAL_RADIUS = 6378136.6
EARTH_POLAR_RADIUS = 6356751.9
EARTH_RATIO = EARTH_EQUATORIAL_RADIUS/EARTH_POLAR_RADIUS
EARTH_SQR_DIFF = EARTH_EQUATORIAL_RADIUS**2 - EARTH_POLAR_RADIUS**2

#################



def floatArguments(func):
    """ A decorator that converts all function arguments to float. 
    
    @param func: a function to be decorated

    @return :[funtion object] the decorated function
    """

    def inner_func(*args):
        args = map(float, args)
        return func(*args)

    return inner_func


def date2JD(year, month, day, hour, minute, second):
    """ Convert date and time to Julian Date with epoch 2000.0. 

    @param year: [int] year
    @param month: [int] month
    @param day: [int] day of the date
    @param hour: [int] hours
    @param minute: [int] minutes
    @param second: [int] seconds

    @return :[float] julian date, epoch 2000.0
    """

    # Create datetime object of current time
    dt = datetime(year, month, day, hour, minute, second)

    # Calculate Julian date
    julian = (dt - JULIAN_EPOCH + J2000_JD)
    
    # Convert seconds to day fractions
    return julian.days + julian.seconds/86400.0


def JD2LST(julian_date, lon):
    """ Convert Julian date to Local Sidreal Time and Greenwich Sidreal Time. 

    @param julian_date: [float] decimal julian date, epoch 2000.0
    @param lon: [float] longitude of the observer in degrees

    @return (LST, GST): [tuple of floats] a tuple of Local Sidreal Time and Greenwich Sidreal Time
    """

    t = (julian_date - J2000_JD.days)/36525

    # Greenwich Sidreal Time
    GST = 280.46061837 + 360.98564736629 * (julian_date - 2451545) + 0.000387933 *t**2 - ((t**3) / 38710000)
    GST = (GST+360) % 360

    # Local Sidreal Time
    LST = (GST + lon + 360) % 360
    
    return LST, GST

@floatArguments
def geo2Cartesian(lon, lat, h, julian_date):
    """ Convert geographical Earth coordinates to Cartesian coordinate system (Earth center as origin).
        The Earth is considered as an elipsoid.

    @param lon: [float] longitde of the observer in degress
    @param lat: [float] latitude of the observer in degrees
    @param h: [int or float] elevation of the observer in meters
    @param julian_date: [float] decimal julian date, epoch 2000.0

    @return (x, y, z): [tuple of floats] a tuple of X, Y, Z Cartesian coordinates
    """

    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)

    # Get Local Sidreal Time
    LST_rad = math.radians(JD2LST(julian_date, lon)[0])

    # Get distance from Earth centre to the position given by geographical coordinates
    Rh = h + math.sqrt(EARTH_POLAR_RADIUS**2 + (EARTH_SQR_DIFF/((EARTH_RATIO * math.tan(lat_rad)) * (EARTH_RATIO * math.tan(lat_rad)) + 1)))

    # Calculate Cartesian coordinates (in meters)
    x = Rh * math.cos(lat_rad) * math.cos(LST_rad)
    y = Rh * math.cos(lat_rad) * math.sin(LST_rad)
    z = Rh * math.sin(lat_rad)

    return x, y, z


def stellar2Vector(ra, dec):
    """ Convert stellar equatorial coordinates to a vector with X, Y and Z components. 

    @param ra: [float] right ascension in degrees
    @param dec: [float] declination in degrees

    @return (x, y, z): [tuple of floats]
    """
    
    ra_rad = math.radians(ra)
    dec_rad = math.radians(dec)

    xt = math.cos(dec_rad) * math.cos(ra_rad)
    yt = math.cos(dec_rad) * math.sin(ra_rad)
    zt = math.sin(dec_rad)

    return xt, yt, zt


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


def cartesian2Geographical(julian_date, lon, Xi, Yi, Zi):
    """ Convert Cartesian coordinates of a point (origin in Earth's centre) to geographical coordinates. 

    @param julian_date: [float] decimal julian date, epoch 2000.0
    @param lon: [float] longitde of the observer in degress
    @param Xi: [float] X coordinate of a point in space (meters)
    @param Yi: [float] Y coordinate of a point in space (meters)
    @param Zi: [float] Z coordinate of a point in space (meters)

    @return (lon_p, lat_p): [tuple of floats]
        lon_p: longitude of the point in degrees
        lat_p: latitude of the point in degrees
    """

    # Get LST and GST
    LST, GST = JD2LST(julian_date, lon)

    # Convert Cartesian coordinates to latitude and longitude
    lon_p = math.degrees(math.atan2(Yi, Xi) - math.radians(GST))
    lat_p = math.degrees(math.atan2(math.sqrt(Xi**2 + Yi**2), Zi))

    return lon_p, lat_p


def triangulate(julian_date, lon1, lat1, h1, ra1, dec1, lon2, lat2, h2, ra2, dec2):
    """ Triangulate a meteor detection point between 2 stations given the station's position and stellar 
        coordinates of the detections.

    @param julian_date: [float] decimal julian date, epoch 2000.0
    @param lon1: [float] longitde of the 1st observer in degress
    @param lat1: [float] latitude of the 1st observer in degrees
    @param h1: [int or float] elevation of the 1st observer in meters
    @param ra1: [float] right ascension of the line of sight from the 1st observer in degrees
    @param dec1: [float] declination of the line of sight from the 1st observer in degrees
    @param lon2: [float] longitde of the 2nd observer in degress
    @param lat2: [float] latitude of the 2nd observer in degrees
    @param h2: [int or float] elevation of the 2nd observer in meters
    @param ra2: [float] right ascension of the line of sight from the 2nd observer in degrees
    @param dec2: [float] declination of the line of sight from the 2nd observer in degrees

    @return (lon_avg, lat_avg, elevation, est_error): [tuple of floats]
        lon_avg: longitude of the midpoint between the 2 estimated points on the lines of sight (degress)
        lat_avg: latitude of the midpoint between the 2 estimated points on the lines of sight (degress)
        elevation: elevation of the point (meters)
        est_error: estimated error of the solution (meters)
    

    """

    # Convert geographical position to Cartesian coordinates for both stations
    X1, Y1, Z1 = geo2Cartesian(lon1, lat1, h1, julian_date)
    X2, Y2, Z2 = geo2Cartesian(lon2, lat2, h2, julian_date)

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
    R_point = math.sqrt(EARTH_POLAR_RADIUS**2 + (EARTH_SQR_DIFF/((EARTH_RATIO * math.tan(math.radians(lat_avg))) * (EARTH_RATIO * math.tan(math.radians(lat_avg))) + 1)))

    # Get points' sea level elevation
    elevation = math.sqrt(Xi_avg**2 + Yi_avg**2 + Zi_avg**2) - R_point

    # Angle of intersection of two vectors (radians)
    angle = math.acos((xt1*xt2 + yt1*yt2 + zt1*zt2) / ((xt1**2 + yt1**2 + zt1**2) * (xt2**2 + yt2**2 + zt2**2)))

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

    ra1 = 71.6 # deg
    dec1 = 23.1 # deg

    # Station 2
    lon2 = 15.964008 # deg
    lat2 = 45.807056 # deg
    h2 = 117 # m

    ra2 = 171.6 # deg
    dec2 = 39 # deg

    ######################

    # Triangulate!
    point_params = triangulate(julian_date, lon1, lat1, h1, ra1, dec1, lon2, lat2, h2, ra2, dec2)

    # Print results
    print 'Longitude: ', point_params[0], ' deg'
    print 'Latitude: ', point_params[1], ' deg'
    print 'Elevation: ', point_params[2], ' m'
    print 'Estimation error +/-: ', point_params[3], ' m'

