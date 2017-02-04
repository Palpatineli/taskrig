#include "sound_device.hpp"
#include <SD.h>
#include <AudioZero.h>
#include "serial_protocol.hpp"

SoundDevice::SoundDevice() {
    AudioZero.begin(44100);
}

uint8_t SoundDevice::register_file(const char* file_name) {
    File sound_file = SD.open(file_name);
    sound_file.close();
    strcpy(files[file_length], file_name);
    file_length++;
    return file_length - 1;
}

void SoundDevice::play(uint8_t audio_id) {
    File audio_file = SD.open(files[audio_id]);
    send_signal(PLAY_SOUND, &audio_id);
    AudioZero.play(audio_file);
    audio_file.close();
}
