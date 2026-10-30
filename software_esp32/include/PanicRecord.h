/**HEADER*******************************************************************
  project : VdMot Controller

  Comments: where the ESP32 crashed, kept over the restart that follows the crash

***************************************************************************/

#pragma once

#include <Arduino.h>

// The panic handler of ESP-IDF is wrapped (linker option -Wl,--wrap=esp_panic_handler): before the normal
// handling (backtrace on the serial port, restart) the crash address, the exception and the backtrace are
// stored in RTC memory, which keeps its content over the restart. After the start they are taken over once.

// description of the crash before this start, e.g. "LoadProhibited at 0x400d1234, address 0x00000000,
// backtrace 0x400d1231 0x400e5675", empty if the last restart was not a crash
String takePanicRecord();
