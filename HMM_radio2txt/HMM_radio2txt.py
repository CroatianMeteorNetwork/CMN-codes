# Copyright 2014 Denis Vida, denis.vida@gmail.com

# The HMM_radio2txt is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, version 2.

# The HMM_radio2txt is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the HMM_radio2txt ; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

from scipy.io.wavfile import read
import numpy as np
import datetime, math

numchunks = 6000
file_name = "RAD_BEDOUR_20111007_0135_BEUCCL_SYS001.wav" #WAV source file name




samprate, wavdata = read(file_name) #Get data from WAV file (samprate = samples/sec), wavdata contains raw levels data


chunks = np.array_split(wavdata, numchunks) #Split array into chunks
dbs = [np.mean(chunk) for chunk in chunks] #Calculate dB values from the mean of the chunks

print samprate

data_file = open('wav_data.txt', 'w')
data_file.write('Sample rate: '+str(samprate)+' samples/sec reduced to '+str(numchunks)+' chunks\n')

for no, line in enumerate(dbs):
	data_file.write(str(no+1)+' '+str(line)+'\n')

data_file.close()
