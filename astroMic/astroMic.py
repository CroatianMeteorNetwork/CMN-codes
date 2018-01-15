"""AstroMic - CMN's tiny tool for audio recording.

Usage:
    astromic devices [-v]
    astromic record <output-rate> <recording-time> <id> [--device=<index>] [--input-rate=<rate>] [--output=<path>]
    astromic (-h | --help)
    astromic --version

Options:
    -h --help               Show this screen.
    --version               Show version.
    -v                      Dump verbose info about listed devices.
    --device=<index>        Use device with specific device index (check "astromic devices" for a list).
    --input-rate=<rate>     Use specific input rate.
    --output=<path>         Specify output directory path.

Output and input rates are specified in Hz. Recording time is in seconds.
"""

import time
import pyaudio
import audioop
import numpy as np
from docopt import docopt

def list_devices(verbose):
    p = pyaudio.PyAudio()

    num = p.get_device_count()
    print("There is " + str(num) + " devices.")

    for i in range(0, num):
        info = p.get_device_info_by_index(i)
        print("Device #" + str(i) + ": " + info["name"] + ". Max input channels: " + str(info["maxInputChannels"]))
        if verbose:
            print(info)
    
    p.terminate()

def start_recording(output_rate, recording_time, def_id, device_index, input_rate, output_path):
    p = pyaudio.PyAudio()

    device = -1
    if device_index == None:
        device = int(p.get_default_input_device_info()["index"])
    else:
        device = int(device_index)

    device_info = p.get_device_info_by_index(device)

    rate = -1
    if input_rate == None:
        rate = int(device_info["defaultSampleRate"])
    else:
        rate = int(input_rate)

    if output_path == None:
        output_path = ""

    output_path += str(def_id) + "-" + time.strftime("%Y%m%d_%H%M%S") + "-"
    
    chunk_size = int(rate / int(output_rate))
    chunks_per_recording = int(recording_time) * rate / chunk_size

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    frames_per_buffer=chunk_size,
                    input=True,
                    input_device_index=device)
    
    samples = np.ndarray(shape=(chunks_per_recording,), dtype=np.int32)
    i = 0
    n = 0
    while True:
        chunk = stream.read(chunk_size)
        samples[i] = audioop.avg(chunk, 2)
        i += 1
        if i == chunks_per_recording:
            save_samples(samples, output_path + str(n) + ".txt")
            i = 0
            n += 1
            samples = np.ndarray(shape=(chunks_per_recording,), dtype=np.int32)

    stream.stop_stream()
    stream.close()
    p.terminate()

def save_samples(samples, filename):
    np.savetxt(filename, samples)
    print("Saved " + filename)

if __name__ == "__main__":
    args = docopt(__doc__, version='AstroMic 1.0')

    if args["devices"]:
        list_devices(args["-v"])
    elif args["record"]:
        start_recording(args["<output-rate>"], args["<recording-time>"], args["<id>"],
            args["--device"], args["--input-rate"], args["--output"])