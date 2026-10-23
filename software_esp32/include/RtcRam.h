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


// set before a restart that keeps the STM32 running, any other value resets it at the start
#define KEEP_STM_RUNNING 0x4B53544DUL

extern RTC_NOINIT_ATTR int readingCnt;
extern RTC_NOINIT_ATTR PI_CONTROL_RTCS piControlRtcs;
extern RTC_NOINIT_ATTR uint32_t keepStmRunning;