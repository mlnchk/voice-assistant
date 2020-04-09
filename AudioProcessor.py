from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub import utils
from pydub import silence

import numpy as np
import math

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

    def __get_chunks(self, chunk_size, left_cut = 0, right_cut = 1):
        if self.aseg is None:
            return None
        aseglen = len(self.aseg)
        l, r = math.floor(aseglen * left_cut), math.ceil(aseglen * right_cut)
        return utils.make_chunks(self.aseg[l:r], chunk_size), (l, r)

    def GetSteps(self, chunk_size):
        chunks, _ = self.__get_chunks(chunk_size)
        step = 1.0 / len(chunks)
        return [[step * i for i in range(len(chunks))], [self.aseg.max * utils.db_to_float(chunk.dBFS) for chunk in chunks]]

    def __get_regions(self, chunk_size, compFunc, left_cut, right_cut):
        chunks, _ = self.__get_chunks(chunk_size, left_cut, right_cut)
        step = (right_cut - left_cut) / len(chunks)
        regions = []
        opened = False
        for i, chunk in enumerate(chunks):
            if compFunc(chunk):
                if opened:
                    regions[len(regions) - 1][1] = i * step + left_cut
                else:
                    opened = True
                    regions.append([i * step + left_cut, i * step + left_cut])
            else:
                opened = False
        return regions

    def GetSilentRegions(self, chunk_size, volume_level, left_cut = 0, right_cut = 1):
        silence_thresh = utils.ratio_to_db(volume_level)

        def compFunc(chunk):
            return chunk.dBFS < silence_thresh

        regions = self.__get_regions(chunk_size, compFunc, left_cut, right_cut)
        y = self.aseg.max * utils.db_to_float(silence_thresh)

        return regions, [[y, y] for i in range(len(regions))]

    def GetNonsilentRegions(self, chunk_size, volume_level, left_cut = 0, right_cut = 1):
        silence_thresh = utils.ratio_to_db(volume_level)

        def compFunc(chunk):
            return chunk.dBFS >= silence_thresh

        regions = self.__get_regions(chunk_size, compFunc, left_cut, right_cut)
        y = self.aseg.max * utils.db_to_float(silence_thresh)

        return regions, [[y, y] for i in range(len(regions))]

    def RemoveSilence(self, volume_level, silence_duration, left_cut, right_cut):
        silence_thresh = utils.ratio_to_db(volume_level)

        chunk_size = 50
        silence_chunks = silence_duration // chunk_size
        chunks, _ = self.__get_chunks(chunk_size, left_cut, right_cut)

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
