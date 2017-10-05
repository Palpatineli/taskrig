#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>
#include "Arduino.h"

// Signal Protocol
const uint8_t SEPARATOR = 0xff;

enum SignalType: uint8_t {
    GIVE_WATER      = 0x00,
    STOP_WATER      = 0x01,
    SEND_TTL        = 0x03,
    LICK_TOUCH      = 0x10,
    SUPPORT_TOUCH   = 0x11,
    LEVER           = 0x12
};

// convenient functions
static uint8_t conversion_buffer[4];

static inline uint8_t* u32tobyte(uint32_t input) {
    conversion_buffer[3] = (uint8_t)input;
    conversion_buffer[2] = (uint8_t)(input >> 8);
    conversion_buffer[1] = (uint8_t)(input >> 16);
    conversion_buffer[0] = (uint8_t)(input >> 24);
    return conversion_buffer;
}

static inline uint8_t* i32tobyte(int32_t input) {
    conversion_buffer[3] = (uint8_t)input;
    conversion_buffer[2] = (uint8_t)(input >> 8);
    conversion_buffer[1] = (uint8_t)(input >> 16);
    conversion_buffer[0] = (uint8_t)(input >> 24);
    return conversion_buffer;
}

static inline int32_t bytetoi32(uint8_t* input) {
    int32_t result = (int32_t)(input[0] << 24 | input[1] << 16 | input[2] << 8 | input[3]);
    return result;
}

static inline uint32_t bytetou32(uint8_t* input) {
    uint32_t result = (uint32_t)(input[0] << 24 | input[1] << 16 | input[2] << 8 | input[3]);
    return result;
}

inline void send_signal(const uint8_t signal_type, uint32_t signal_value) {
    Serial.write(SEPARATOR);
    Serial.write(signal_type);
    Serial.write(u32tobyte(millis()), 4);
    Serial.write(u32tobyte(signal_value), 4);
}

inline void send_signal(const uint8_t signal_type, int32_t signal_value) {
    Serial.write(SEPARATOR);
    Serial.write(signal_type);
    Serial.write(u32tobyte(millis()), 4);
    Serial.write(i32tobyte(signal_value), 4);
}

inline uint32_t receive_signal(uint8_t* signal_type, uint8_t* signal_value) {
    uint32_t available = Serial.available();
    uint32_t result_count = 0;
    if (available > 2) {
        while (Serial.read() != SEPARATOR) {available--;}
        result_count = (available + 1) / 3;
        signal_type[0] = Serial.read();
        signal_value[0] = Serial.read();
        for (uint32_t idx = 1; idx < result_count; idx++) {
            Serial.read();
            signal_type[idx] = Serial.read();
            signal_value[idx] = Serial.read();
        }
        return result_count;
    } else return 0;
}
