from pydub import AudioSegment
from pydub.silence import split_on_silence

import numpy as np

MIN_SILENCE_LEN = 2000

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

    def RemoveSilence(self, volume_level):
        aseg = self.aseg
        silence_thresh = 20*np.log10(volume_level)
        chunks = split_on_silence(aseg, min_silence_len = MIN_SILENCE_LEN, silence_thresh = silence_thresh)
        chunkslastindex = len(chunks) - 1
        silence_chunk = AudioSegment.silent(duration=500)
        result = AudioSegment.empty()
        for i, chunk in enumerate(chunks):
            if i > 0:
                result += silence_chunk
            result += chunk
            if i < chunkslastindex:
                result += silence_chunk
        if len(result.raw_data) > 0:
            self.aseg = result
