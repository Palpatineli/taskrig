#include "Arduino.h"
#include <SPI.h>
#include "ads1262.hpp"
#include "../pinDef.hpp"

static const uint32_t MAX_SPI = 7273800;
static const uint8_t COMMAND_RESET=0x07;
static const uint8_t COMMAND_START=0x09;
static const uint8_t COMMAND_STOP=0x0B;


ADS1262::ADS1262() : config{false, true, true, ADS1262_Config::CHECK_SUM, true, ADS1262_Config::NO_CHOP, ADS1262_Config::SINC1,
                            false, ADS1262_Config::X32, ADS1262_Config::R400, ADS1262_Config::AIN6, ADS1262_Config::AIN7} {
    // *RESET/*PWDN is pulled high, so the chip should be running whenever there is power.
    SPI.begin();
    init_spi();
    init_gpio();
    start(false);
}

ADS1262::~ADS1262() {
    start(false);
    SPI.endTransaction();
    SPI.end();
}

void ADS1262::init_spi() {
    SPI.beginTransaction(SPISettings(MAX_SPI, MSBFIRST, SPI_MODE1));
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, LOW);
}

void ADS1262::init_gpio() {
    pinMode(ADC_START, OUTPUT);
    pinMode(ADC_READY, INPUT);
}

Status ADS1262::pack_status(uint8_t status_char) {
    Status status{(status_char & 0x40) != 0, (status_char & 0x10) != 0, (status_char & 0x02) != 0};
    return status;
}


int ADS1262::check_id() {
    uint8_t id;
    read_register(0x00, 1, &id);
    if ((id >> 5) != 0x00) return 1;
    return 0;
}

int ADS1262::reset() {
    uint8_t command = COMMAND_RESET;
    SPI.transfer(&command, 1);
    return 0;
}

void ADS1262::read_register(uint8_t register_addr, uint32_t len, uint8_t *buffer) {
    uint8_t *op_buffer = new uint8_t[len + 2];
    op_buffer[0] = 0x20 | register_addr;
    op_buffer[1] = len - 1;
    SPI.transfer(op_buffer, len + 2);
    memcpy(buffer, op_buffer + 2, len * sizeof(uint8_t));
    delete [] op_buffer;
}

void ADS1262::write_register(uint8_t register_addr, uint8_t* value, uint8_t len) {
    if (len > 0x1F) len = 0x1F;
    uint8_t *op_buffer = new uint8_t[len + 2];
    memcpy(op_buffer + 2, value, len * sizeof(uint8_t));
    op_buffer[0] = 0x40 | register_addr;
    op_buffer[1] = len - 1;
    SPI.transfer(op_buffer, len + 2);
    delete [] op_buffer;
}

void ADS1262::write_config() {
    uint8_t config_char[6];
    config_char[0] |= ((config.level_shift_bias_enable << 1) | config.internal_reference_enable);
    config_char[1] |= ((config.data_has_status_bit << 2) | config.data_check_mode);
    config_char[2] |= (((!config.continuous) << 6) | config.chop_mode << 4);
    config_char[3] |= (config.filter_mode << 5);
    config_char[4] |= ((config.pga_bypass << 7) | (config.pga_gain << 4) | config.sample_rate);
    config_char[5] |= ((config.positive << 4) | config.negative);
    write_register(MAIN_REGISTER_ADDRS, config_char, 6);
}

void ADS1262::start(bool start_stop) {
    digitalWrite(ADC_START, start_stop?HIGH:LOW);
}

bool ADS1262::check_done() {
    return digitalRead(ADC_READY) == LOW;
}

inline bool verify_checksum(uint8_t* packet, uint8_t packet_size) {
    uint8_t checksum {0};
    for (uint8_t idx = 0; idx < packet_size - 1; idx++) checksum += packet[idx];
    return (checksum + 0x9b == packet[packet_size - 1]);
}

int32_t ADS1262::read() {
    uint8_t buffer[data_length]{};
    SPI.transfer(buffer, data_length);
    if ((!(*buffer & 0x40)) || verify_checksum(buffer, data_length)) return -1;
    uint8_t *input = buffer + 1;
    return (int32_t)(input[0] << 24 | input[1] << 16 | input[2] << 8 | input[3]);
}

