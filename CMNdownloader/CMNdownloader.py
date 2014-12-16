# Copyright 2014 Emil Siladji

# The CMNdownloader is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, version 2.

# The CMNdownloader is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the CMNdownloader ; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import urllib
import urllib2
import time
from PIL import Image as img
import os
import errno
from urllib2 import urlopen
from bs4 import BeautifulSoup
from datetime import timedelta, date, datetime


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def convert_to_jpg(name, dir_timestamp):
    mkdir_p(dir_timestamp)
    radar_img = img.open(name)
    name_jpg = name.split('.')
    name_jpg = name_jpg[0] + '.jpg'
    radar_img.save(dir_timestamp + '\\' + name_jpg)
    os.remove(name)


def downloader(image_name, image_url, dir_name, fo):
    try:
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        image_name = timestamp + '_' + image_name + '.png' 
        if fo:
            dir_timestamp = dir_name + os.sep + str(date.today() - timedelta(days=1))
        else:
            dir_timestamp = dir_name + os.sep + timestamp.split('_')[0]
        f = open(image_name, 'wb')
        f.write(urllib.urlopen(image_url).read())
        f.close()
        convert_to_jpg(image_name, dir_timestamp)
        if fo:
            print image_name + ' (Fireball orbits) successfully downloaded.'
        else:
            print image_name + ' successfully downloaded.'
    except:
        print '!ERROR: ' + image_name + 'could not be retrieved at ' + timestamp


def shower_radiants_data(dir_name):
    try:
        soup = BeautifulSoup(urlopen("http://fireballs.ndc.nasa.gov/cmor-radiants/earth.html"))
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        with open(dir_name + os.sep + timestamp.split('_')[0] + os.sep + timestamp + '_shower_radiants_data.txt', "w") as text_file:
            text_file.write(soup.pre.get_text())
        print timestamp + ' shower radiants data successfully downloaded'
    except:
            print '!ERROR: shower radiants data could not be retrieved at ' + timestamp


def fireball_orbits(dir_name):
    try:
        yesterday = date.today() - timedelta(days=1)
        yesterday_date = datetime.strftime(yesterday, '%Y%m%d')
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        soup = BeautifulSoup(urlopen("http://fireballs.ndc.nasa.gov/" + yesterday_date + ".html"))
        for event in soup.findAll('a', href=True, text='SUMMARY'):
            downloader(event['href'].split("/")[2],"http://fireballs.ndc.nasa.gov/" + event['href'], dir_name, True)
    except:
        print '!ERROR: (Fireball orbits) events could not be retrieved at ' + timestamp
    
    try:
        for orbit in soup.findAll('a', href=True, text='ORBIT'):
            with open(dir_name + os.sep + str(yesterday) + os.sep + timestamp + orbit['href'].split("/")[2] + '_orbit.txt', "w") as text_file:
                text_file.write(urllib2.urlopen('http://fireballs.ndc.nasa.gov/' + orbit['href']).read())
        print timestamp + ' (Fireball orbits) orbit data successfully downloaded.'
    except:
        print '!ERROR: (Fireball orbits) orbit data could not be retrieved at ' + timestamp


def repeating_6h():
    downloader("skymap-activity","http://fireballs.ndc.nasa.gov/cmor-radiants/skymap-activity.png", "HMM downloads", False)
    downloader("skymap-velocity","http://fireballs.ndc.nasa.gov/cmor-radiants/skymap-velocity.png", "HMM downloads", False)

    downloader("equatorial","http://fireballs.ndc.nasa.gov/cmor-radiants/equatorial.png", "HMM downloads", False)
    downloader("scecliptic","http://fireballs.ndc.nasa.gov/cmor-radiants/scecliptic.png", "HMM downloads", False)
    shower_radiants_data("HMM downloads")

    time.sleep(21590) #5h:59min:50sec


while True:
    fireball_orbits("Fireball orbits (ASGARD)")
    repeating_6h()
    repeating_6h()
    repeating_6h()
    repeating_6h()