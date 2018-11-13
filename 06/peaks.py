from sys import argv
from numpy import abs, mean, fft
from wave import open
from struct import unpack


class PeaksCalculator:
    def __init__(self, filename):
        self.WAV_FILE = open(filename, 'rb')
        self.CHANNELS_COUNT = self.WAV_FILE.getnchannels()
        self.SAMPLE_WIDTH = self.WAV_FILE.getsampwidth()
        self.FRAME_RATE = self.WAV_FILE.getframerate()
        self.FRAME_COUNT = self.WAV_FILE.getnframes()
        self.STRUCT_FORMAT = '<' + ('h' * self.CHANNELS_COUNT * self.FRAME_RATE)

        self.low = None
        self.high = None
        self._calculate_peaks()

    @staticmethod
    def _get_amplitudes(ft_result):
        amplitudes = []
        for i in range(len(ft_result)):
            amplitudes.append(abs(ft_result[i]))
        return amplitudes

    def get_peaks(self):
        return self.low, self.high

    def _calculate_peaks(self):
        while self.WAV_FILE.tell() < self.FRAME_COUNT:
            self._process_frame()

    def _should_process(self, frames_length):
        return frames_length == self.SAMPLE_WIDTH * self.CHANNELS_COUNT * self.FRAME_RATE

    def _set_peaks(self, amplitudes, avg):
        avg_check = avg * 20
        for i, amplitude in enumerate(amplitudes):
            if amplitude >= avg_check:
                if self.high is None or self.high < i:
                    self.high = i
                if self.low is None or self.low > i:
                    self.low = i

    def _process_frame(self):
        frames = self.WAV_FILE.readframes(self.FRAME_RATE)
        if self._should_process(len(frames)):
            d_frames = unpack(self.STRUCT_FORMAT, frames)
            ft_array = []
            for i in range(0, len(d_frames), 2):
                ft_array.append((d_frames[i] + d_frames[i+1]) / 2.0)
            ft_result = fft.rfft(ft_array)
            amplitudes = self._get_amplitudes(ft_result)
            avg = mean(amplitudes)
            self._set_peaks(amplitudes, avg)

    def __str__(self):
        if self.high is None or self.low is None:
            return 'no peaks'
        return 'low = %s, high = %s' % (self.low, self.high)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.WAV_FILE.close()


def main():
    filename = argv[1]
    with PeaksCalculator(filename) as pc:
        print(pc)


if __name__ == '__main__':
    main()
