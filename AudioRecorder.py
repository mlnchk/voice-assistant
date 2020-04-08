import sounddevice as sd
import soundfile as sf
import threading
import tempfile
import queue
import sys
import os

class AudioRecorder:
    devices = sd.query_devices()
    device = sd.query_devices(kind = 'input')

    def __init__(self, statusCallback):
        self.filename = None
        self.__recording = False
        self.statusCallback = statusCallback
        self.fileClosed = True

    def flush_last(self):
        if self.filename is None:
            return
        os.remove(self.filename)
        self.filename = None
    
    def if_fileClosed(self):
        return self.fileClosed

    def get_filename(self):
        return self.filename

    def get_devices(self):
        return self.devices

    def get_device(self):
        return self.device

    def set_device(self, device):
        self.device = device

    def record(self):
        device_info = sd.query_devices(self.device['name'], 'input')
        samplerate = int(device_info['default_samplerate'])
        self.file = tempfile.NamedTemporaryFile(
            prefix='rec_unlimited_',
            suffix='.wav',
            delete=False
        )
        self.fileClosed = False
        self.filename = self.file.name
        channels = 1
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                self.stop()
                self.statusCallback()
            else:
                q.put(indata.copy())

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(self.file, mode='x', samplerate=samplerate, channels=channels) as file:
            with sd.InputStream(samplerate=samplerate, device=self.device['name'], channels=channels, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                while self.__recording:
                    file.write(q.get())
                print('\nRecording finished: ' + repr(self.filename))
        self.file.close()
        self.fileClosed = True

    def start(self):
        self.flush_last()
        self.__recording = True
        self.loop_thread = threading.Thread(target=self.record)
        self.loop_thread.start()

    def stop(self):
        self.__recording = False
