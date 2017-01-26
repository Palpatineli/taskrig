from typing import Dict

import pkg_resources
from pyglet import media


class QuickSound(object):
    _sounds = dict()

    def __init__(self, sound_files: Dict[str, str]):
        resource_package = 'plptn.taskrig'
        resource_path = '/'.join(('data', 'sound'))
        for sound_id in ["reward", "punish", "start"]:
            temp_path = '/'.join((resource_path, sound_files[sound_id]))
            file_path = pkg_resources.resource_filename(resource_package, temp_path)
            self._sounds[sound_id] = media.load(file_path, streaming=False)

    def __del__(self):
        for sound_id, sound in self._sounds.items():
            del sound

    def __contains__(self, item):
        return item in self._sounds

    def play(self, sound_id: str):
        self._sounds[sound_id].play()
