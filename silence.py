from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub import utils
from pydub import silence

import numpy as np

MIN_SILENCE_LEN = 2000

class AudioProcessor():

    aseg = None
    filename = None

    def Open(self, filename):
        self.aseg = AudioSegment.from_file(filename, format="wav")
        
        self.filename = filename
    
    def Save(self):
        if self.filename is None:
            return
        self.aseg.export(self.filename, format="wav")

    def Close(self):
        self.filename = None
        self.aseg = None

    def GetData(self):
        if self.aseg is None:
            return None
        return abs(np.fromstring(self.aseg.raw_data, 'Int16'))

    def __get_chunks(self, chunk_size):
        if self.aseg is None:
            return None
        return utils.make_chunks(self.aseg, chunk_size)

    def GetSteps(self, chunk_size):
        chunks = self.__get_chunks(chunk_size)
        step = 1.0 / len(chunks)
        return [[step * i for i in range(len(chunks))], [self.aseg.max * utils.db_to_float(chunk.dBFS) for chunk in chunks]]

    def GetSilentRegions(self, chunk_size, volume_level):
        silence_thresh = utils.ratio_to_db(volume_level)
        chunks = self.__get_chunks(chunk_size)
        step = 1.0 / len(chunks)
        regions = []
        opened = False
        for i, chunk in enumerate(chunks):
            if chunk.dBFS < silence_thresh:
                if opened:
                    regions[len(regions) - 1][1] = i * step
                else:
                    opened = True
                    regions.append([i * step, i * step])
            else:
                opened = False
        y = self.aseg.max * utils.db_to_float(silence_thresh)
        return regions, [[y, y] for i in range(len(regions))]


    def RemoveSilence(self, volume_level, silence_duration):
        silence_thresh = utils.ratio_to_db(volume_level)

        chunk_size = 50
        silence_chunks = silence_duration // chunk_size
        chunks = self.__get_chunks(chunk_size)

        result = AudioSegment.empty()
        opened = False
        silence_len = 0
        for chunk in chunks:
            if chunk.dBFS >= silence_thresh:
                if not opened:
                    opened = True
                    silence_len = 0
                result += chunk
            else:
                opened = False
                silence_len += 1
                if silence_len <= silence_chunks:
                    result += chunk

        if len(result.raw_data) > 0:
            self.aseg = result
