#include "clock.hpp"
#include "Arduino.h"

void Clock::push(TimedEvent event) {
    data.to_begin();
    while (data.to_next()) {
        if (data.get_value().timestamp > event.timestamp) {
            data.insert_prev(event);
            return;
        }
    }
    data.insert_next(event);
}

List<Event> Clock::check() {
    List<Event> time_out;
    if (data.is_empty()) return time_out;
    auto current_time = millis();
    data.to_begin();
    while ((!data.is_empty()) && (data.get_value().timestamp <= current_time)) {
        time_out.insert_next(data.get_value().event);
        data.remove();
    }
    return time_out;
}
