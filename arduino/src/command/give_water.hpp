#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include "../command.hpp"

class Clock;

class GiveWater: public Command {
public:
    GiveWater();
    uint8_t run(uint8_t duration, Clock *clk);
};


class StopWater: public Command {
    uint8_t run(uint8_t duration, Clock *clk);
};
