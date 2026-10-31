#include "globals.h"
#include "RtcRam.h"

#include <stddef.h>

RTC_NOINIT_ATTR RTC_RAM rtcRam;
int &readingCnt = rtcRam.readingCnt;
PI_CONTROL_RTCS &piControlRtcs = rtcRam.piControlRtcs;
uint32_t &keepStmRunning = rtcRam.keepStmRunning;

static_assert(sizeof(PANIC_RECORD) == 0x38, "RTC layout changed");
static_assert(offsetof(RTC_RAM, keepStmRunning) == 0x38, "RTC layout changed");
static_assert(offsetof(RTC_RAM, piControlRtcs) == 0x3c, "RTC layout changed");
static_assert(offsetof(RTC_RAM, readingCnt) == 0x1ec, "RTC layout changed");