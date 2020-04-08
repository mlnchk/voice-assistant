from pydub import AudioSegment
from pydub.silence import split_on_silence

import numpy as np

MIN_SILENCE_LEN = 2000 # At least 2000 ms long.
SILENCE_THRESH = -80 # Consider a chunk silent if it's quieter than -50 dBFS.

class AudioProcessor():

    aseg = None

    def Open(self, filename):
        self.aseg = AudioSegment.from_file(filename, format="wav")
    
    def Close(self):
        self.aseg = None

    def GetData(self):
        if self.aseg is None:
            return None
        return abs(np.fromstring(self.aseg.raw_data, 'Int16'))

# Normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

def remove_silence(filename, volume_level):
    aseg = AudioSegment.from_file(filename, format="wav")
    print(aseg.max_dBFS, aseg.max, volume_level)
    # Split track where the silence is 2 seconds or more and get chunks
    chunks = split_on_silence(aseg, min_silence_len = MIN_SILENCE_LEN, silence_thresh = SILENCE_THRESH)
    result = AudioSegment.empty()

    # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
    silence_chunk = AudioSegment.silent(duration=500)
    # Process each chunk with your parameters
    for i, chunk in enumerate(chunks):
        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk
        # Normalize the entire chunk.
        # normalized_chunk = match_target_amplitude(audio_chunk, -20.0)
        result += audio_chunk
    # result.export("no_silence_" + filename.split('/')[-1], format="wav")
