/**HEADER*******************************************************************
  project : VdMot Controller

  Comments: where the ESP32 crashed, kept over the restart that follows the crash

***************************************************************************/

#include <stddef.h>
#include "PanicRecord.h"
#include "esp_attr.h"
#include "esp_debug_helpers.h"
#include "esp_private/panic_internal.h"
#include "soc/cpu.h"
#include "soc/soc_memory_types.h"
#include "xtensa/corebits.h"
#include "xtensa/xtensa_context.h"

#define PANIC_RECORD_MAGIC  0x50414E43UL
#define PANIC_BACKTRACE     8

typedef struct {
  uint32_t magic;
  uint32_t exception;                   // panic_exception_t: fault, abort, watchdog, ...
  uint32_t exccause;                    // Xtensa exception cause of a fault
  uint32_t pc;                          // instruction that crashed
  uint32_t excvaddr;                    // address it accessed
  uint32_t backtrace[PANIC_BACKTRACE];  // as on the serial port, 0 = end
  uint32_t check;
} PANIC_RECORD;

// not initialized at the start, after power on the content is random: only valid with magic and check
static RTC_NOINIT_ATTR PANIC_RECORD panicRecord;

static inline __attribute__((always_inline)) uint32_t panicCheck(const PANIC_RECORD *record)
{
  const uint32_t *words = (const uint32_t *) record;
  uint32_t sum = 0x5A5A5A5AUL;
  for (size_t i = 0; i < offsetof(PANIC_RECORD, check) / sizeof(uint32_t); i++) {
    sum = ((sum << 5) | (sum >> 27)) ^ words[i];
  }
  return sum;
}

extern "C" void __real_esp_panic_handler(panic_info_t *info);

// Runs inside the panic handler, the watchdogs are already set to restart the chip if it hangs.
// The flash cache may be off: only code in IRAM, no strings, no library calls except the stack walk
// of ESP-IDF that the normal handler uses for its backtrace as well.
extern "C" void IRAM_ATTR __wrap_esp_panic_handler(panic_info_t *info)
{
  const XtExcFrame *frame = (const XtExcFrame *) info->frame;

  panicRecord.magic = 0;
  panicRecord.exception = (uint32_t) info->exception;
  panicRecord.pc = (uint32_t) info->addr;
  panicRecord.exccause = frame ? frame->exccause : 0;
  panicRecord.excvaddr = frame ? frame->excvaddr : 0;
  // volatile, so the compiler does not turn the loop into a call of memset
  volatile uint32_t *backtrace = panicRecord.backtrace;
  for (int i = 0; i < PANIC_BACKTRACE; i++) backtrace[i] = 0;

  if (frame) {
    esp_backtrace_frame_t stack;
    stack.pc = (uint32_t) frame->pc;
    stack.sp = (uint32_t) frame->a1;
    stack.next_pc = (uint32_t) frame->a0;
    stack.exc_frame = frame;
    bool sane = esp_stack_ptr_is_sane(stack.sp);
    int n = 0;
    panicRecord.backtrace[n++] = esp_cpu_process_stack_pc(stack.pc);
    while (sane && (n < PANIC_BACKTRACE) && (stack.next_pc != 0)) {
      sane = esp_backtrace_get_next_frame(&stack);
      panicRecord.backtrace[n++] = esp_cpu_process_stack_pc(stack.pc);
    }
  }

  panicRecord.check = panicCheck(&panicRecord);
  panicRecord.magic = PANIC_RECORD_MAGIC;

  __real_esp_panic_handler(info);
}

static const char *panicName(uint32_t exception, uint32_t exccause)
{
  switch (exception) {
    case PANIC_EXCEPTION_DEBUG:    return "Debug exception";
    case PANIC_EXCEPTION_IWDT:     return "Interrupt watchdog";
    case PANIC_EXCEPTION_TWDT:     return "Task watchdog";
    case PANIC_EXCEPTION_ABORT:    return "abort()";
    default: break;
  }
  switch (exccause) {
    case EXCCAUSE_ILLEGAL:           return "IllegalInstruction";
    case EXCCAUSE_INSTR_ERROR:       return "InstructionFetchError";
    case EXCCAUSE_LOAD_STORE_ERROR:  return "LoadStoreError";
    case EXCCAUSE_DIVIDE_BY_ZERO:    return "IntegerDivideByZero";
    case EXCCAUSE_UNALIGNED:         return "LoadStoreAlignment";
    case EXCCAUSE_INSTR_PROHIBITED:  return "InstrFetchProhibited";
    case EXCCAUSE_LOAD_PROHIBITED:   return "LoadProhibited";
    case EXCCAUSE_STORE_PROHIBITED:  return "StoreProhibited";
    default:                         return nullptr;
  }
}

String takePanicRecord()
{
  PANIC_RECORD record = panicRecord;
  panicRecord.magic = 0;
  if ((record.magic != PANIC_RECORD_MAGIC) || (record.check != panicCheck(&record))) return "";

  char buf[40];
  const char *name = panicName(record.exception, record.exccause);
  if (name) {
    snprintf(buf, sizeof(buf), "%s", name);
  } else {
    snprintf(buf, sizeof(buf), "Exception %u", (unsigned) record.exccause);
  }
  String result = String(buf);
  snprintf(buf, sizeof(buf), " at 0x%08x", (unsigned) record.pc);
  result += buf;
  if (record.exception == PANIC_EXCEPTION_FAULT) {
    snprintf(buf, sizeof(buf), ", address 0x%08x", (unsigned) record.excvaddr);
    result += buf;
  }
  result += ", backtrace";
  for (int i = 0; (i < PANIC_BACKTRACE) && (record.backtrace[i] != 0); i++) {
    snprintf(buf, sizeof(buf), " 0x%08x", (unsigned) record.backtrace[i]);
    result += buf;
  }
  return result;
}
