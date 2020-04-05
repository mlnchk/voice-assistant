import sounddevice as sd
import soundfile as sf
import threading

import argparse
import tempfile
import queue
import sys

class StopAudio(Exception):
    pass

parser = argparse.ArgumentParser(description=__doc__)

class AudioRecorder:
    devices = sd.query_devices()
    device = sd.query_devices(kind = 'input')

    def __init__(self, filename):
        self.filename = filename
        self.__recording = False

    def get_devices(self):
        return self.devices

    def get_device(self):
        return self.device

    def set_device(self, device):
        self.device = device

    def record(self):
        try:
            device_info = sd.query_devices(self.device['name'], 'input')
            samplerate = int(device_info['default_samplerate'])
            filename = tempfile.mktemp(prefix='rec_unlimited_', suffix='.wav', dir='')
            channels = 1
            q = queue.Queue()

            def callback(indata, frames, time, status):
                """This is called (from a separate thread) for each audio block."""
                if status:
                    print(status, file=sys.stderr)
                q.put(indata.copy())

            # Make sure the file is opened before recording anything:
            with sf.SoundFile(filename, mode='x', samplerate=samplerate, channels=channels) as file:
                with sd.InputStream(samplerate=samplerate, device=self.device['name'], channels=channels, callback=callback):
                    print('#' * 80)
                    print('press Ctrl+C to stop the recording')
                    print('#' * 80)
                    while self.__recording:
                        file.write(q.get())
                    print('\nRecording finished: ' + repr(filename))

    def start(self):
        self.__recording = True
        self.loop_thread = threading.Thread(target=self.record)
        self.loop_thread.start()

    def stop(self):
        print('ass')
        self.__recording = False
