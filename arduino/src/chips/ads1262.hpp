#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>

typedef struct Status_ {
    bool is_new;
    bool low_ref_alarm;
    bool pga_alarm;
} Status;

typedef struct ADS1262_Config_ {
    // power
    bool level_shift_bias_enable;
    bool internal_reference_enable;
    // interface
    bool data_has_status_bit;
    enum CheckMode: uint8_t {NO_CHECK=0, CHECK_SUM=1, CRC=2} data_check_mode;
    // mode0
    bool continuous;
    enum ChopMode: uint8_t {NO_CHOP=0, CHOP=1, IDAC=2, CHOP_IDAC=3} chop_mode;
    // mode1
    enum FilterMode: uint8_t {SINC1=0, SINC2=1, SINC3=2, SINC4=3, FIR=4} filter_mode;
    // mode2 (skip sensor bias config)
    bool pga_bypass;
    enum PgaGain: uint8_t {X1=0, X2=1, X4=2, X8=3, X16=4, X32=5} pga_gain;
    enum SampleRate: uint8_t {R2_5=0, R5=1, R10=2, R16_6=3, R20=4, R50=5, R60=6, R100=7, R400=8, R1200=9, R2400=10,
                              R4800=11, R7200=12, R14400=13, R19200=14, R38400=15} sample_rate;
    // multiplexer
    enum Pin: uint8_t {AIN0=0, AIN1=1, AIN2=2, AIN3=3, AIN4=4, AIN5=5, AIN6=6, AIN7=7, AIN8=8, AIN9=9,
                       AINCOM=10, TEMP=11, AVDD=12, DVDD=13, TDAC=14, NC=15} positive;
    Pin negative;
} ADS1262_Config;

class ADS1262 {
public:
    ADS1262();
    virtual ~ADS1262();

    void read_register(uint8_t register_addr, uint32_t len, uint8_t *buffer);
    void write_register(uint8_t register_addr, uint8_t* value, uint8_t len);
    void write_config();

    int check_id();
    int reset();
    void start(bool start_stop);

    bool check_done();
    int32_t read();
    ADS1262_Config config;
    static Status pack_status(uint8_t status_char);

protected:
    static const uint32_t data_length = 6;
    static const uint8_t MAIN_REGISTER_ADDRS = 0x01;
    uint8_t buffer[50];

    void init_spi();
    void init_gpio();
};
