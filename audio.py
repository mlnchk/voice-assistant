import argparse
import tempfile
import queue
import sys
import sounddevice as sd
import soundfile as sf
from silence import remove_silence

class StopAudio(Exception):
    pass

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def get_devices():
    devices = sd.query_devices()
    return devices

def record_audio():
    try:
        device_info = sd.query_devices(args.device, 'input')
        samplerate = int(device_info['default_samplerate'])
        filename = tempfile.mktemp(prefix='rec_unlimited_', suffix='.wav', dir='')
        q = queue.Queue()
        channels = 1

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(filename, mode='x', samplerate=samplerate, channels=channels) as file:
            with sd.InputStream(samplerate=args.samplerate, channels=channels, callback=callback):
                print('*' * 80)
                print('press Ctrl+C to stop the recording')
                print('*' * 80)
                while True:
                    file.write(q.get())

    except KeyboardInterrupt:
        print('\nRecording finished: ' + repr(args.filename))
        remove_silence(args.filename)
        return
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))
        return

def cli(args):
    try:
        if args.list_devices:
            print(get_devices())
            parser.exit(0)
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])
        if args.filename is None:
            args.filename = tempfile.mktemp(prefix='rec_unlimited_',
                                            suffix='.wav', dir='')
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                        channels=args.channels, subtype=args.subtype) as file:
            with sd.InputStream(samplerate=args.samplerate, device=args.device,
                                channels=args.channels, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                while True:
                    file.write(q.get())

    except KeyboardInterrupt:
        print('\nRecording finished: ' + repr(args.filename))
        remove_silence(args.filename)
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))
    

def main_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    parser.add_argument(
        '-c', '--channels', type=int, default=1, help='number of input channels')
    parser.add_argument(
        'filename', nargs='?', metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
    args = parser.parse_args()
    cli(args)
