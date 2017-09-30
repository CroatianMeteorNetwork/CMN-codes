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

# Astronomical units in kilometers
AU = 149597870.7

# Gravitational constant of the Sun in km^3/s^2
SUN_MU = 1.32712440018e11

# Mass of the Sun in kilograms
SUN_MASS = 1.98855e+30

# Gravitational constant in m^3/kg/s^2
G = 6.67384e-11

# Earth's sidereal year in days
SIDEREAL_YEAR = 365.256363004

# Obliquity of the Earth at J2000.0 epoch
J2000_OBLIQUITY = math.radians(23.4392911111)

# Define Julian epoch
JULIAN_EPOCH = datetime(2000, 1, 1, 12) # J2000.0 noon
J2000_JD = timedelta(2451545) # J2000.0 epoch in julian days

class EARTH_CONSTANTS(object):
    """ Holds Earth's shape parameters. """

    def __init__(self):

        # Earth elipsoid parameters in meters (source: WGS84, the GPS standard)
        self.EQUATORIAL_RADIUS = 6378137.0
        self.POLAR_RADIUS = 6356752.314245
        self.E = math.sqrt(1.0 - self.POLAR_RADIUS**2/self.EQUATORIAL_RADIUS**2)
        self.RATIO = self.EQUATORIAL_RADIUS/self.POLAR_RADIUS
        self.SQR_DIFF = self.EQUATORIAL_RADIUS**2 - self.POLAR_RADIUS**2

# Initialize Earth shape constants object
EARTH = EARTH_CONSTANTS()


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


def jd2LST(julian_date, lon):
    """ Convert Julian date to Local Sidereal Time and Greenwich Sidereal Time. 

    Source: J. Meeus: Astronomical Algorithms

    Arguments:
        julian_date: [float] decimal julian date, epoch J2000.0
        lon: [float] longitude of the observer in degrees
    
    Return:
        (LST, GST): [tuple of floats] a tuple of Local Sidereal Time and Greenwich Sidereal Time
    """

    t = (julian_date - J2000_JD.days)/36525.0

    # Greenwich Sidereal Time
    GST = 280.46061837 + 360.98564736629*(julian_date - J2000_JD.days) + 0.000387933*t**2 - (t**3)/38710000
    GST = (GST + 360)%360

    # Local Sidereal Time
    LST = (GST + lon + 360)%360
    
    return LST, GST


def latLonAlt2ECEF(lat, lon, h):
    """ Convert geographical coordinates to Earth centered - Earth fixed coordinates.

    Arguments:
        lat: [float] latitude in radians (+north)
        lon: [float] longitude in radians (+east)
        h: [float] elevation in meters

    Return:
        (x, y, z): [tuple of floats] ECEF coordinates

    """

    # Get distance from Earth centre to the position given by geographical coordinates, in WGS84
    N = EARTH.EQUATORIAL_RADIUS/math.sqrt(1.0 - (EARTH.E**2)*math.sin(lat)**2)

    # Calculate ECEF coordinates
    ecef_x = (N + h)*math.cos(lat)*math.cos(lon)
    ecef_y = (N + h)*math.cos(lat)*math.sin(lon)
    ecef_z = ((1 - EARTH.E**2)*N + h)*math.sin(lat)

    return ecef_x, ecef_y, ecef_z


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

    # Get Local Sidereal Time
    LST_rad = math.radians(jd2LST(julian_date, lon)[0])

    ecef_x, ecef_y, ecef_z = latLonAlt2ECEF(lat_rad, lon_rad, h)

    # Calculate the Earth radius at given latitude
    Rh = math.sqrt(ecef_x**2 + ecef_y**2 + ecef_z**2)

    # Calculate the geocentric latitude (latitude which considers the Earth as an elipsoid)
    lat_geocentric = math.atan2(ecef_z, math.sqrt(ecef_x**2 + ecef_y**2))

    # Calculate Cartesian ECI coordinates (in meters)
    x = Rh*math.cos(lat_geocentric)*math.cos(LST_rad)
    y = Rh*math.cos(lat_geocentric)*math.sin(LST_rad)
    z = Rh*math.sin(lat_geocentric)

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




def ecef2LatLonAlt(x, y, z):
    """ Convert Earth centered - Earth fixed coordinates to geographical coordinates (latitude, longitude, 
        elevation).

    Arguments:
        x: [float] ECEF x coordinate
        y: [float] ECEF y coordinate
        z: [float] ECEF z coordinate

    Return:
        (lat, lon, alt): [tuple of floats] latitude and longitude in radians, elevation in meters

    """

    # Calculate the polar eccentricity
    ep = math.sqrt((EARTH.EQUATORIAL_RADIUS**2 - EARTH.POLAR_RADIUS**2)/(EARTH.POLAR_RADIUS**2))

    # Calculate the longitude
    lon = math.atan2(y, x)

    p = math.sqrt(x**2  +  y**2);

    theta = math.atan2( z*EARTH.EQUATORIAL_RADIUS, p*EARTH.POLAR_RADIUS)

    # Calculate the latitude
    lat = math.atan2(z + (ep**2)*EARTH.POLAR_RADIUS*math.sin(theta)**3, 
        p - (EARTH.E**2)*EARTH.EQUATORIAL_RADIUS*math.cos(theta)**3)

    # Get distance from Earth centre to the position given by geographical coordinates, in WGS84
    N = EARTH.EQUATORIAL_RADIUS/math.sqrt(1.0 - (EARTH.E**2)*math.sin(lat)**2)

    # Calculate the height in meters
    alt = p/math.cos(lat) - N

    # Handle the case when in the Southern hemisphere
    if( abs(x) < 1  and  abs(y) < 1):
        alt = abs(z) - EARTH.POLAR_RADIUS

    return lat, lon, alt


def LST2LongitudeEast(julian_date, LST):
    """ Convert Julian date and Local Sidereal Time to east longitude. 
    
    Arguments:
        julian_date: [float] decimal julian date, epoch J2000.0
        LST: [float] Local Sidereal Time in degrees

    Return:
        lon: [float] longitude of the observer in degrees
    """

    t = (julian_date - J2000_JD.days)/36525.0

    # Greenwich Sidereal Time
    GST = 280.46061837 + 360.98564736629*(julian_date - J2000_JD.days) + 0.000387933*t**2 - (t**3)/38710000
    GST = (GST + 360)%360

    # Calculate longitude
    lon = (LST - GST + 180)%360 - 180

    return lon, GST


def cartesian2Geo(julian_date, x, y, z):
    """ Convert Cartesian ECI coordinates of a point (origin in Earth's centre) to geographical coordinates.
    
    Arguments:
        julian_date: [float] decimal julian date
        X: [float] X coordinate of a point in space (meters)
        Y: [float] Y coordinate of a point in space (meters)
        Z: [float] Z coordinate of a point in space (meters)
    
    Return:
        (lon, lat, ele): [tuple of floats]
            lon: longitude of the point in radians
            lat: latitude of the point in radians
            ele: elevation in meters
    """


    # Calculate LLA
    lat, r_LST, ele = ecef2LatLonAlt(x, y, z)

    # Calculate proper longitude from the given JD
    lon, _ = LST2LongitudeEast(julian_date, math.degrees(r_LST))

    # Convert longitude to radians
    lon = math.radians(lon)

    # # Get LST and GST
    # LST, GST = jd2LST(julian_date, lon)

    # # Convert Cartesian coordinates to latitude and longitude
    # lon_p = math.degrees(math.atan2(Yi, Xi) - math.radians(GST))
    # lat_p = math.degrees(math.atan2(math.sqrt(Xi**2 + Yi**2), Zi))

    return lat, lon, ele



### Precession ###

def equatorialCoordPrecession(start_epoch, final_epoch, ra, dec):
    """ Corrects Right Ascension and Declination from one epoch to another, taking only precession into 
        account.

        Implemented from: Jean Meeus - Astronomical Algorithms, 2nd edition, pages 134-135
    
    Arguments:
        start_epoch: [float] Julian date of the starting epoch
        final_epoch: [float] Julian date of the final epoch
        ra: [float] non-corrected right ascension in degrees
        dec: [float] non-corrected declination in degrees
    
    Return:
        (ra, dec): [tuple of floats] precessed equatorial coordinates in degrees

    """

    ra = math.radians(ra)
    dec = math.radians(dec)

    T = (start_epoch - J2000_JD.days)/36525.0
    t = (final_epoch - start_epoch)/36525.0

    # Calculate correction parameters
    zeta  = ((2306.2181 + 1.39656*T - 0.000139*T**2)*t + (0.30188 - 0.000344*T)*t**2 + 0.017998*t**3)/3600
    z     = ((2306.2181 + 1.39656*T - 0.000139*T**2)*t + (1.09468 + 0.000066*T)*t**2 + 0.018203*t**3)/3600
    theta = ((2004.3109 - 0.85330*T - 0.000217*T**2)*t - (0.42665 + 0.000217*T)*t**2 - 0.041833*t**3)/3600

    # Convert parameters to radians
    zeta, z, theta = map(math.radians, (zeta, z, theta))

    # Calculate the next set of parameters
    A = math.cos(dec)  *math.sin(ra + zeta)
    B = math.cos(theta)*math.cos(dec)*math.cos(ra + zeta) - math.sin(theta)*math.sin(dec)
    C = math.sin(theta)*math.cos(dec)*math.cos(ra + zeta) + math.cos(theta)*math.sin(dec)

    # Calculate right ascension
    ra_corr = math.atan2(A, B) + z

    # Calculate declination (apply a different equation if close to the pole, closer then 0.5 degrees)
    if (math.pi/2 - abs(dec)) < math.radians(0.5):
        dec_corr = math.arccos(math.sqrt(A**2 + B**2))
    else:
        dec_corr = math.asin(C)

    # Wrap right ascension to [0, 2*pi] range
    ra_corr = ra_corr%(2*math.pi)

    # Wrap declination to [-pi/2, pi/2] range
    dec_corr = (dec_corr + math.pi/2)%math.pi - math.pi/2

    return math.degrees(ra_corr), math.degrees(dec_corr)
    


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
    lat_avg, lon_avg, elevation = cartesian2Geo(julian_date, Xi_avg, Yi_avg, Zi_avg)

    # Angle of intersection of two vectors (radians)
    angle = math.acos((xt1*xt2 + yt1*yt2 + zt1*zt2) / ((xt1**2 + yt1**2 + zt1**2) * (xt2**2 + yt2**2 + zt2**2)))

    # Estimated error
    est_error = d / 2 / math.sin(angle)


    return math.degrees(lon_avg), math.degrees(lat_avg), elevation, est_error
    


if __name__ == '__main__':

    ### INPUT PARAMETERS ###
    # year, month, day, hours, minutes, seconds
    julian_date = date2JD(2017, 5, 31, 21, 46, 18)

    # Station 1
    lon1 = 13.721672 # deg
    lat1 = 45.275964 # deg
    h1 = 218 # m

    ra1 = 311.975 # deg
    dec1 = 15.089 # deg

    # Station 2
    lon2 = 14.482893 # deg
    lat2 = 45.325099 # deg
    h2 = 210 # m

    ra2 = 307.580 # deg
    dec2 = 19.200 # deg

    ######################

    # # Precess ra, dec
    # ra1, dec1 = equatorialCoordPrecession(J2000_JD.days, julian_date, ra1, dec1)
    # ra2, dec2 = equatorialCoordPrecession(J2000_JD.days, julian_date, ra2, dec2)

    # Triangulate!
    point_params = triangulate(julian_date, lon1, lat1, h1, ra1, dec1, lon2, lat2, h2, ra2, dec2)

    # Print results
    print 'Longitude: ', point_params[0], ' deg'
    print 'Latitude: ', point_params[1], ' deg'
    print 'Elevation: ', point_params[2], ' m'
    print 'Estimation error +/-: ', point_params[3], ' m'