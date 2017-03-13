#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>

class String;

const uint8_t FILE_LIST_SIZE{16};

class SoundDevice {
public:
    explicit SoundDevice();
    ~SoundDevice();
    uint8_t register_file(const char* file_name);
    void play(uint8_t audio_id);
protected:
    String *files[FILE_LIST_SIZE];
    uint8_t file_list_len;
};
