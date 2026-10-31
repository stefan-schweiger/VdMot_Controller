#pragma once

#include "globals.h"

#define RTC_RAM_PATTERN "RTCPattern001"

typedef struct {
  char pattern[15];  
  float target;
  float value;
  float iProp;
  float esum;
  float lastControlPosition;
} PI_CONTROL_RTC;

typedef struct {
    PI_CONTROL_RTC piControlRtc[ACTUATOR_COUNT];
} PI_CONTROL_RTCS;


#define PANIC_BACKTRACE     8

// where the ESP32 crashed, see PanicRecord.cpp
typedef struct {
  uint32_t magic;
  uint32_t exception;                   // panic_exception_t: fault, abort, watchdog, ...
  uint32_t exccause;                    // Xtensa exception cause of a fault
  uint32_t pc;                          // instruction that crashed
  uint32_t excvaddr;                    // address it accessed
  uint32_t backtrace[PANIC_BACKTRACE];  // as on the serial port, 0 = end
  uint32_t check;
} PANIC_RECORD;

// set before a restart that keeps the STM32 running, any other value resets it at the start
#define KEEP_STM_RUNNING 0x4B53544DUL

// Everything in RTC memory in one struct: the linker places separate variables in an order of its own.
// An update must not move them, the old firmware hands keepStmRunning and the PI states over at the restart.
// The order is the one of firmware 929c3b7 (rtcRam starts at 0x50000200), new members only at the end.
typedef struct {
  PANIC_RECORD panicRecord;             // 0x50000200
  uint32_t keepStmRunning;              // 0x50000238
  PI_CONTROL_RTCS piControlRtcs;        // 0x5000023c
  int readingCnt;                       // 0x500003ec
} RTC_RAM;

extern RTC_NOINIT_ATTR RTC_RAM rtcRam;
extern int &readingCnt;
extern PI_CONTROL_RTCS &piControlRtcs;
extern uint32_t &keepStmRunning;