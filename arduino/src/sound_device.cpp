#include "sound_device.hpp"
#include <SD.h>
#include <SPI.h>
#include <AudioZero.h>
#include "serial_protocol.hpp"

static const uint8_t CHIP_SELECT = 28;

SoundDevice::SoundDevice(): file_list_len(0) {
    if (!SD.begin(CHIP_SELECT)) Serial.println("SD device initialization failure");
}

SoundDevice::~SoundDevice() {
    for (uint8_t idx = 0; idx < FILE_LIST_SIZE; idx++) {
        if (files[idx] != nullptr) delete files[idx];
    }
}

uint8_t SoundDevice::register_file(const char* file_name) {
    File sound_file = SD.open(file_name);
    if (!sound_file) Serial.println("failed to open audio file");
    sound_file.close();
    files[file_list_len] = new String(file_name);
    file_list_len++;
    return file_list_len - 1;
}

void SoundDevice::play(uint8_t audio_id) {
    File sound_file = SD.open(*(files[audio_id]));
    if (!sound_file) Serial.println("failed to open audio file");
    AudioZero.begin(2*44100);
    send_signal(SignalType::PLAY_SOUND, (uint32_t)audio_id);
    AudioZero.play(sound_file);
    AudioZero.end();
    sound_file.close();
}
