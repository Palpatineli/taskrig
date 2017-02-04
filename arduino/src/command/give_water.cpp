#include "give_water.hpp"
#include "../pinDef.hpp"
#include "../clock.hpp"
#include "../serial_protocol.hpp"

uint8_t GiveWater::run(uint8_t duration, Clock *clk) {
    clk->push({duration, {STOP_WATER, 0}});
    digitalWrite(PWM_PIN, HIGH);
    digitalWrite(CTRL_PIN, HIGH);
    uint8_t signal = 0;
    send_signal(WATER_STAMP, &signal);
    return 0;
}

uint8_t StopWater::run(uint8_t duration, Clock *clk) {
    digitalWrite(PWM_PIN, LOW);
    digitalWrite(CTRL_PIN, LOW);
    return 0;
}
