Meteor Triangulation
=========

Meteor Triangulation module provides an analytical way (line of sight method) to triangulate a point in space from individual detection points of a meteor.

See function 'triangulate' for details about the usage. Also, an example of usage is given inside the script in the __main__ part.

Input parameters:
- Time of observation (year, month, day, hour, minute, second)
- Station A position (longitude, latitude, elevation)
- Station A line fo sight (procession corrected RA and Dec, epoch 2000.0)
- Station B position (longitude, latitude, elevation)
- Station B line fo sight (procession corrected RA and Dec, epoch 2000.0)

Output:
- Position (longitude, latitude, elevation) of the triangulated point
- Error estimation in meters