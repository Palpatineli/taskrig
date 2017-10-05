#include "Arduino.h"
#include "src/chip/fdc1004.hpp"
#include "src/chip/ads1262.hpp"
#include "src/pinDef.hpp"
#include "src/clock.hpp"
#include "src/command.hpp"
#include "src/serial_protocol.hpp"
#include "src/command/give_water.hpp"
#include "src/command/send_trigger.hpp"

FDC1004 *touch;
ADS1262 *lever;
Clock *clk_1;
volatile bool recording(false);
uint32_t baudrate(115200);
static const uint8_t COMMAND_SIZE = 8, SIGNAL_QUEUE_SIZE = 255;
Command *commands[COMMAND_SIZE];
uint8_t signal_type[SIGNAL_QUEUE_SIZE];  // looks like arduino has problem with newed arrays
uint8_t signal_value[SIGNAL_QUEUE_SIZE];
int32_t voltage_read;
uint8_t status_byte;

void dispatch(Event event, Clock *clk) {
    Command *temp = commands[event.type];
    uint8_t result = temp->run(event.parameter, clk);
    if (result != 0) {
        if (result == COM_STOP_RECORDING) recording = false;
        else if (result == COM_START_RECORDING) recording = true;
    }
}

void setup() {
    Serial.begin(baudrate);
    while (!Serial);  // limitation of Arduino Zero software usb, you have to wait
    clk_1 = new Clock();
    touch = new FDC1004();
    lever = new ADS1262();
    commands[SignalType::GIVE_WATER] = new GiveWater();
    commands[SignalType::STOP_WATER] = new StopWater();
    commands[SignalType::SEND_TTL] = new SendTrigger();
    delay(250);
    uint8_t raw_config[6];
    lever->write_config(raw_config);
    for (int idx = 0; idx < 6; idx++) {
        send_signal(SignalType::LEVER, (uint32_t)raw_config[idx]);
    }
}

void loop() {
    uint32_t signal_count = receive_signal(signal_type, signal_value);
    for (uint32_t idx = 0; idx < signal_count; idx++) {
        dispatch({signal_type[idx], signal_value[idx]}, clk_1);
    }
    auto clock_events = clk_1->check();
    if (!clock_events.is_empty()) {
        clock_events.to_begin();
        dispatch(clock_events.get_value(), clk_1);
        while(clock_events.to_next()) dispatch(clock_events.get_value(), clk_1);
    }

    if (touch->check_done()) {
        send_signal(SignalType::LICK_TOUCH, (int32_t)touch->read_measurement(0));
        send_signal(SignalType::SUPPORT_TOUCH, (int32_t)touch->read_measurement(1));
    }
    voltage_read = 127;
    uint8_t lever_status = lever->read(&voltage_read);
    if (lever_status == 0) {
        send_signal(SignalType::LEVER, voltage_read);
    }
}

