#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>

class SoundDevice {
public:
    explicit SoundDevice();
    uint8_t register_file(const char* file_name);
    void play(uint8_t audio_id);
protected:
    char files[16][100];
    uint8_t file_length;
};
