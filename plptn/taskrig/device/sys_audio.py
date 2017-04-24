import wave as audio
from functools import partial
from os.path import isfile, join

from PyQt5.QtCore import QTimer, QObject, pyqtSlot
from pkg_resources import resource_filename, Requirement
from pyaudio import PyAudio, paContinue, Stream

WAVE_FOLDER = "plptn/taskrig/data/sound"
EXTENSION = ".wav"
SOUND_ID = ('start', 'reward', 'punish')


def _audio_callback(in_file, in_data, frame_count, time_info, status):
    return in_file.readframes(frame_count), paContinue


class SysAudio(QObject):
    files = dict()
    stream = None  # type: Stream
    timer = None  # type: QTimer

    def __init__(self):
        super(SysAudio, self).__init__()
        for sound_id in SOUND_ID:
            file_path = self._get_path(sound_id)
            if isfile(file_path):
                self.files[sound_id] = file_path
            else:
                raise ValueError("{0}{1} audio file does not exist".format(sound_id, EXTENSION))
        self.audio = PyAudio()
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.cleanup)
        self.is_playing = False

    @staticmethod
    def _get_path(file_name: str) -> str:
        return resource_filename(Requirement.parse("taskrig"),
                                 join(WAVE_FOLDER, file_name + EXTENSION))

    @staticmethod
    def _open_audio_stream(audio_port: PyAudio, audio_file: audio.Wave_read, **kwargs):
        return audio_port.open(format=audio_port.get_format_from_width(audio_file.getsampwidth()),
                               channels=audio_file.getnchannels(), rate=audio_file.getframerate(),
                               output=True, **kwargs)

    def play(self, sound_id: str):
        if self.is_playing:
            self.cleanup()
        audio_file = audio.open(self.files[sound_id], 'rb')
        self.stream = self._open_audio_stream(self.audio, audio_file,
                                              stream_callback=partial(_audio_callback, audio_file))
        self.stream.start_stream()
        self.is_playing = True
        self.timer.start()

    @pyqtSlot(name="cleanup")
    def cleanup(self):
        if self.is_playing and self.stream and not self.stream.is_active():
            self.timer.stop()
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.is_playing = False


if __name__ == '__main__':
    print(isfile(resource_filename(Requirement.parse("taskrig"), join(WAVE_FOLDER, "punish.wav"))))
