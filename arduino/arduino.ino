 #include "Arduino.h"
#include "src/chips/fdc1004.hpp"
#include "src/chips/ads1262.hpp"
#include "src/pinDef.hpp"
#include "src/sound_device.hpp"
#include "src/clock.hpp"
#include "src/command.hpp"
#include "src/serial_protocol.hpp"
#include "src/command/give_water.hpp"
#include "src/command/play_sound.hpp"

FDC1004 *touch;
ADS1262 *lever;
Clock *clock;
volatile bool recording(false);
uint8_t AUDIO_START, AUDIO_REWARD, AUDIO_PUNISH;
uint32_t baudrate(115200);
static const uint8_t COMMAND_SIZE = 8;
Command *commands[COMMAND_SIZE];

void dispatch(Event event, Clock *clk) {
    uint8_t result = commands[event.type]->run(event.parameter, clk);
    if (result != 0) {
        if (result == COM_STOP_RECORDING) recording = false;
        else if (result == COM_START_RECORDING) recording = true;
    }
}

void setup() {
    touch = new FDC1004();
    lever = new ADS1262();
    clock = new Clock();
    pinMode(PWM_PIN, OUTPUT);
    pinMode(CTRL_PIN, OUTPUT);
    commands[GIVE_WATER] = new GiveWater();
    commands[STOP_WATER] = new StopWater();
    SoundDevice *sound_dev = new SoundDevice();
    AUDIO_START = sound_dev->register_file("start.wav");
    AUDIO_REWARD = sound_dev->register_file("reward.wav");
    AUDIO_PUNISH = sound_dev->register_file("punish.wav");
    commands[PLAY_SOUND] = new PlaySound(sound_dev);
    Serial.begin(baudrate);
}

void loop() {
    uint8_t *signal_type, *signal_value;
    uint32_t signal_count = receive_signal(signal_type, signal_value);
    for (uint32_t idx = 0; idx < signal_count; idx++) dispatch({signal_type[idx], signal_value[idx]}, clock);
    auto clock_events = clock->check();
    if (!clock_events.is_empty()) {
        clock_events.to_begin();
        while(clock_events.to_next()) dispatch(clock_events.get_value(), clock);
    }
    if (touch->check_done()) {
        send_signal(TOUCH_CHAN_0, i32tobyte(touch->read_measurement(0)));
        send_signal(TOUCH_CHAN_1, i32tobyte(touch->read_measurement(1)));
    }
    if (lever->check_done()) send_signal(LEVER, i32tobyte(lever->read()));
}
