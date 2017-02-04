#include "fdc1004.hpp"
#include <Wire.h>

static const uint8_t CONFIG_REGISTER = 0x0c;
static const uint8_t MSB_REGISTERS[4] = {0x00, 0x02, 0x04, 0x06};
static const uint8_t LSB_REGISTERS[4] = {0x01, 0x03, 0x05, 0x07};
static const uint8_t MEASUREMENT_REGISTERS[4] = {0x08, 0x09, 0x0A, 0x0B};
static const uint8_t OFFSET_REGISTERS[4] = {0x0D, 0x0E, 0x0F, 0x10};
static const uint8_t GAIN_REGISTERS[4] = {0x11, 0x12, 0x13, 0x14};
static const uint8_t FDC1004_ADDRESS = 0x50;
static const uint8_t ID_REGISTERS[2] = {0xFE, 0xFF};
static const uint8_t DEVICE_ID[]{0x10, 0x04};
static const uint8_t MANUFACTURER[]{'T', 'I'};

FDC1004::FDC1004() {
    Wire.begin();
    Wire.setClock(400000);
    set_measurement(0, {Measurement::SINGLE, 1, {0}});
    set_measurement(1, {Measurement::SINGLE, 2, {0}});
    write_config({FDC1004_Config::TWO_HUNDRED, true, {true, true, false, false}});
}

FDC1004::~FDC1004() {
    write_config({FDC1004_Config::TWO_HUNDRED, false, {true, true, false, false}});
}

inline void read_register(uint8_t register_addr, uint8_t size, uint8_t *buffer) {
    Wire.beginTransmission(FDC1004_ADDRESS);
    Wire.write(register_addr);
    Wire.requestFrom(FDC1004_ADDRESS, size);
    for (int idx = 0; idx < size; idx ++) buffer[idx] = Wire.read();
    Wire.endTransmission();
}

int FDC1004::check_id() {
    int result = 0;
    uint8_t buffer[2];
    read_register(ID_REGISTERS[0], 2, buffer);
    if ((buffer[0] != MANUFACTURER[0]) || (buffer[1] != MANUFACTURER[1])) return 1;
    read_register(ID_REGISTERS[1], 2, buffer);
    if ((buffer[0] != DEVICE_ID[0]) || (buffer[1] != DEVICE_ID[1])) return 2;
    return 0;
}

int FDC1004::set_measurement(uint8_t id, Measurement setting) {
    uint8_t buffer[3];
    buffer[0] = MEASUREMENT_REGISTERS[id];
    if (setting.channel_positive > 3) return 1;
    switch (setting.measure_type) {
    case Measurement::SINGLE:
        buffer[1] = uint8_t((setting.channel_positive) << 5) | 0x1c;
        buffer[2] = 0x00;
        break;
    case Measurement::DIFF:
        if (setting.channel_negative > 3) return 1;
        buffer[1] = uint8_t((setting.channel_positive) << 5) | uint8_t((setting.channel_negative - 1) << 2);
        buffer[2] = 0x00;
        break;
    case Measurement::OFFSET:
        if (setting.offset > 96.875 || setting.offset < 0) return 1;
        uint8_t offset = uint8_t(setting.offset / 3.125);
        buffer[1] = uint8_t((setting.channel_positive) << 5) | 0x10 | offset >> 3;
        buffer[2] = uint8_t(offset << 5);
        break;
    }
    Wire.write(buffer, 3);
    return 0;
}

void FDC1004::write_config(FDC1004_Config config) {
    uint8_t buffer[3];
    buffer[0] = CONFIG_REGISTER;
    buffer[1] = uint8_t(config.rate << 2) | config.repeat;
    buffer[2] = 0;
    for (size_t i = 0; i < 4; i++) {
        if (config.enable[i]) buffer[2] |= (0x80 >> i);
    }
    Wire.write(buffer, 3);
}

int FDC1004::set_offset(int channel_id, double offset) {
    uint16_t offset_int = uint16_t(offset * 0x800);
    uint8_t buffer[] {OFFSET_REGISTERS[channel_id], uint8_t(offset_int >> 8), uint8_t(offset_int & 0xFF)};
    Wire.write(buffer, 3);
    return 0;
}

int FDC1004::set_gain(int channel_id, double gain) {
    uint16_t gain_int = uint16_t(gain * 0x4000);
    uint8_t buffer[] {GAIN_REGISTERS[channel_id], uint8_t(gain_int >> 8), uint8_t(gain_int & 0xFF)};
    Wire.write(buffer, 3);
    return 0;
}

bool FDC1004::check_done() {
    uint8_t buffer[2];
    read_register(CONFIG_REGISTER, 2, buffer);
    return buffer[1] & (0x08);
}

int32_t FDC1004::read_measurement(const uint8_t id) {
    uint8_t msb[2]; uint8_t lsb[2];
    read_register(MSB_REGISTERS[id], 2, msb);
    read_register(LSB_REGISTERS[id], 2, lsb);
    if (msb[0] & 0x80) return -((msb[0] & 0x7f) << 16 | msb[1] << 8 | lsb[0]);
    else return (msb[0] << 16 | msb[1] << 8 | lsb[0]);  // 24 bit two-complement coding
}

int FDC1004::reset() {
    uint8_t buffer[3];
    read_register(CONFIG_REGISTER, 2, buffer + 1);
    buffer[0] = CONFIG_REGISTER;
    buffer[1] |= 0x80;
    Wire.write(buffer, 3);
    return 0;
}
