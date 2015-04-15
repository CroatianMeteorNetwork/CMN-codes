import serial
import time
import matplotlib.pyplot as plt
import numpy as np

def waitResponse():
    # Wait for response from Arduino while toggling iris
    while 1:
     if "Response" in ser.readline():
        break

# Length of test in seconds
test_time = 10.0


# Initalize serial connection
ser = serial.Serial('COM4', 115200, timeout=0)

# Wait for initialization
time.sleep(2)

# Open iris
ser.write("1")
waitResponse()

# Wait for the iris to open
time.sleep(2)

print 'Connected!'

data_array = np.array([], dtype=np.uint16)
times_array = np.array([], dtype=np.float32)
counter = 0

first_read = True 
while 1:
    #start_time = time.clock()
    
    if not first_read:
        if (time.clock() - test_start >= test_time):
            break
                
    try:
        b1 = ord(ser.read(1))
        b2 = ord(ser.read(1))
    except:
        continue

    # Calculate ADC value from 2 bytes transfered via COM interface
    serial_value = b1 + b2*256
    if serial_value != '':
        if first_read:
            first_read = False
            test_start = time.clock()
            print 'start', test_start

        #print serial_value

        # Add value to data list
        try:

            # Numpy arrays
            data_array = np.append(data_array, [serial_value])
            times_array = np.append(times_array, [counter])

            counter += 1

        except:
            print 'Error!'
            print serial_value
            break
        # Add time to list
        #times_list.append(time.clock() - test_start)

test_duration = time.clock() - test_start

# Close iris
ser.write("0");
waitResponse()

# Close serial communication
ser.close()

# Samples per second
sps = len(data_array) / test_duration

print 'Calculated SPS: ', sps

# Calculate times from counter values
times_array = times_array/sps

print data_array[500:510]
print 'max:', max(data_array)
plt.plot(times_array, data_array)

plt.ylim((0, 4096))
plt.show()