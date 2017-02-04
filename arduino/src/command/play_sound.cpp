#include "play_sound.hpp"
#include "../sound_device.hpp"
#include "../clock.hpp"

PlaySound::PlaySound(SoundDevice *sound_dev) {
    sound_device = sound_dev;
}

uint8_t PlaySound::run(uint8_t id, Clock *clk) {
    sound_device->play(id);
    return 0;
}
