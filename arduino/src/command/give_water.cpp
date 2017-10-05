#include "give_water.hpp"
#include "../pinDef.hpp"
#include "../clock.hpp"
#include "../serial_protocol.hpp"

GiveWater::GiveWater() {
    pinMode(PinID::CTRL_PIN, OUTPUT);
}

uint8_t GiveWater::run(uint8_t duration, Clock *clk) {
    if (duration > 0) clk->push({millis() + duration, {SignalType::STOP_WATER, 0}});
    digitalWrite(PinID::CTRL_PIN, HIGH);
    uint8_t signal = 0;
    send_signal(SignalType::GIVE_WATER, (uint32_t)signal);
    return 0;
}

uint8_t StopWater::run(uint8_t duration, Clock *clk) {
    digitalWrite(PinID::CTRL_PIN, LOW);
    return 0;
}
