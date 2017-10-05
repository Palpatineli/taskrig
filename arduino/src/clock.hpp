#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>
#include "linkedlist.hpp"

typedef struct Event_ {
    uint8_t type;
    uint8_t parameter;
} Event;

typedef struct TimedEvent_ {
    uint32_t timestamp;
    Event event;
} TimedEvent;

class Clock {
public:
    Clock() = default;
    List<Event> check();
    void push(TimedEvent event);

protected:
    List<TimedEvent> data;
};
