import time
import urllib
import urllib2
import os

def call_timer():
	time.sleep(900)

def current_date_time():
	folder_name, timeHM = time.strftime("%Y-%m-%d"), time.strftime("%H_%M")
	return folder_name, timeHM

def download_CMOR(folder_name, timeHM):
	path_exists(folder_name)
	location_activity = folder_name + "/" + "activity_" + timeHM + ".png"
	location_velocity = folder_name + "/" + "velocity_" + timeHM + ".png"
	urllib.urlretrieve("http://fireballs.ndc.nasa.gov/cmor-radiants/skymap-activity.png", location_activity)
	urllib.urlretrieve("http://fireballs.ndc.nasa.gov/cmor-radiants/skymap-velocity.png", location_velocity)
	print "Slike skinute " + folder_name + " u (HH_MM): " + timeHM	

def path_exists(path):
    try: 
    	os.makedirs(path)
    except OSError:
    	if not os.path.isdir(path):
        	raise

def test_connection():
    try:
        response=urllib2.urlopen('http://fireballs.ndc.nasa.gov/cmor-radiants/',timeout=10)
        return True
    except urllib2.URLError as err: pass
    return False

while True:
	if test_connection():
		folder_name, timeHM = current_date_time()
		download_CMOR(folder_name, timeHM)
		call_timer()
	else:
		print "Neuspjesno povezivanje " + time.strftime("%Y-%m-%d %H:%M:%S")
		call_timer()