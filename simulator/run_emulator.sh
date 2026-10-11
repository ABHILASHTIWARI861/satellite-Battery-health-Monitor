#!/bin/bash
# Runs the real firmware on an emulated ATmega328P (simavr) and exposes its UART as tcp://127.0.0.1:PORT
# Needs: simavr libsimavr-dev libelf-dev gcc   (Ubuntu/WSL: sudo apt install simavr libsimavr-dev libelf-dev gcc)
set -e
cd "$(dirname "$0")"
PORT=${1:-7777}
[ -f build/firmware.elf ] || ./build_firmware.sh
[ -x build/avr_host ] || gcc -O2 -I/usr/include/simavr -I/usr/include/simavr/avr avr_host.c -o build/avr_host -lsimavr -lelf -lm
echo "[*] Pin edges are logged to simulator/build/pins.log"
exec build/avr_host build/firmware.elf "$PORT" build/pins.log
