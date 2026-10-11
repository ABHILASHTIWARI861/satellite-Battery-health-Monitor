#!/bin/bash
# Compile the project's REAL Arduino sketch for an ATmega328P (Arduino Uno).
# Needs: gcc-avr, avr-libc  (Ubuntu/WSL: sudo apt install gcc-avr avr-libc)
# Output: simulator/build/firmware.elf  and  firmware.hex   (the .hex is what Wokwi loads)
set -e
cd "$(dirname "$0")"
INO="../arduino/satellite_hitl_controller/satellite_hitl_controller.ino"
CACHE=".cache"; CORE_DIR="$CACHE/ArduinoCore-avr-master"
if [ ! -d "$CORE_DIR" ]; then
  mkdir -p "$CACHE"
  echo "[*] Downloading official Arduino AVR core (one time)..."
  curl -sL https://codeload.github.com/arduino/ArduinoCore-avr/tar.gz/refs/heads/master | tar xz -C "$CACHE"
fi
CORE="$CORE_DIR/cores/arduino"; VAR="$CORE_DIR/variants/standard"; OUT=build; mkdir -p $OUT
FLAGS="-mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10819 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR -Os -w -ffunction-sections -fdata-sections -I$CORE -I$VAR"
for f in $CORE/*.c;   do avr-gcc $FLAGS -std=gnu11 -c "$f" -o $OUT/$(basename "$f").o; done
for f in $CORE/*.cpp; do avr-g++ $FLAGS -std=gnu++11 -fno-exceptions -fno-threadsafe-statics -c "$f" -o $OUT/$(basename "$f").o; done
for f in $CORE/*.S;   do avr-gcc $FLAGS -x assembler-with-cpp -c "$f" -o $OUT/$(basename "$f").o; done
# .ino -> .cpp the way the Arduino IDE does it (header + prototypes for this sketch's functions)
{ echo '#include <Arduino.h>'; echo 'void processCommand(String cmd); void updateHardwareActuation();'; cat "$INO"; } > $OUT/sketch.cpp
avr-g++ $FLAGS -std=gnu++11 -fno-exceptions -c $OUT/sketch.cpp -o $OUT/sketch.o
avr-g++ -mmcu=atmega328p -Wl,--gc-sections -o $OUT/firmware.elf $OUT/*.o -lm
avr-objcopy -O ihex -R .eeprom $OUT/firmware.elf $OUT/firmware.hex
avr-size $OUT/firmware.elf
