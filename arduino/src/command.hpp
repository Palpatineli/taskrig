#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>

const uint8_t COM_START_RECORDING = 2, COM_STOP_RECORDING = 1;
class Clock;

class Command {
public:
    virtual uint8_t run(uint8_t param, Clock *clock) = 0;
};
