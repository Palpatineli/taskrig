#pragma clang diagnostic ignored "-Wc++11-extensions"
#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>

typedef struct Measurement_ {
    enum {DIFF, SINGLE, OFFSET} measure_type;
    char channel_positive;  // channels 1-4
    union {
        char channel_negative;  // channels 1-4
        float offset;  // in pF, between 0 and 96.875pF
    };
} Measurement;

typedef struct FDC1004_Config_ {
    enum : uint8_t {ONE_HUNDRED = 1, TWO_HUNDRED = 2, FOUR_HUNDRED = 3} rate;  // sampling rate
    bool repeat;
    bool enable[4];
} FDC1004_Config;

class FDC1004 {
public:
    explicit FDC1004();
    virtual ~FDC1004();

    bool check_done();
    int32_t read_measurement(const uint8_t id);
    int set_measurement(uint8_t measurement_id, Measurement setting);
    void write_config(FDC1004_Config config);
    int set_offset(int channel_id, double offset);  // in pF, between 0 and 16pF, in steps of 0.000488
    int set_gain(int channel_id, double gain);  // between 0 and 4, in steps of 6.10E-5
    int check_id();
    int reset();
};
