from scipy.io.wavfile import read
import datetime

file_name = "RAD_BEDOUR_20111007_0135_BEUCCL_SYS001.wav" #WAV source file name

samprate, wavdata = read(file_name) #Get data from WAV file (samprate = samples/sec), wavdata contains raw levels data


print samprate

data_file = open('wav_data.txt', 'w')
data_file.write('Sample rate: '+str(samprate)+' samples/sec\n')

for no, line in enumerate(wavdata):
	data_file.write(str(no+1)+' '+str(line)+'\n')

data_file.close()