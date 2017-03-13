#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include "../command.hpp"

class SoundDevice;
class Clock;

class PlaySound: virtual public Command {
public:
    explicit PlaySound(SoundDevice *sound_dev);
    uint8_t run(uint8_t audio_id, Clock *clk);
private:
    SoundDevice *sound_device;
};
