#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include "../command.hpp"

class Clock;

class GiveWater: virtual public Command {
    virtual uint8_t run(uint8_t duration, Clock *clk);
};
class StopWater: virtual public Command {
    virtual uint8_t run(uint8_t duration, Clock *clk);
};
