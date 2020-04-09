from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub import utils
from pydub import silence

import numpy as np
import math

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
        return [[step * i for i in range(len(chunks))], [chunk.rms for chunk in chunks]]

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

    def GetSilentRegions(self, chunk_size, volume_level, left_cut = 0, right_cut = 1, min_nonsilence_len = 0):
        def compFunc(chunk):
            return chunk.dBFS < utils.ratio_to_db(volume_level)

        regions = self.__get_regions(chunk_size, compFunc, left_cut, right_cut)
        if min_nonsilence_len > 0:
            space = min_nonsilence_len / len(self.aseg)
            return self.__min_space_len(regions, space)
        return regions

    def GetNonsilentRegions(self, chunk_size, volume_level, left_cut = 0, right_cut = 1, min_silence_len = 0):
        def compFunc(chunk):
            return chunk.dBFS >= utils.ratio_to_db(volume_level)

        regions = self.__get_regions(chunk_size, compFunc, left_cut, right_cut)
        if min_silence_len > 0:
            space = min_silence_len / len(self.aseg)
            return self.__min_space_len(regions, space)
        return regions

    def __min_space_len(self, regions, length):
        newregions = [regions[0]]
        cur_end = regions[0][1]
        for region in regions[1:]:
            if region[0] - cur_end > length:
                newregions[len(newregions) - 1][1] += length / 2
                newregions.append([region[0] - length / 2, region[1]])
                cur_end = region[1]
            else:
                newregions[len(newregions) - 1][1] = region[1]
                cur_end = region[1]
        return newregions

    def Cut(self, regions):
        fact = len(self.aseg)
        result = AudioSegment.empty()
        for reg in regions:
            result += self.aseg[reg[0] * fact : reg[1] * fact]
        if len(result) > 0:
            self.aseg = result