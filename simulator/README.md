# Real-firmware simulation (no hardware needed)

This folder runs the project's **actual** `satellite_hitl_controller.ino` (compiled for an ATmega328P)
on an emulated Arduino Uno and connects it to the Python HITL bridge over a serial link.

```
Python pipeline / dashboard ──(HITLSerialBridge, 115200 8N1)──► emulated Arduino Uno running the real .ino
        "<1,4,2>\n"                                           ◄── "<ACK,1,4,2,uptime_ms>"   (uptime = firmware millis())
```

## Option A — Local emulator (simavr), Linux / macOS / WSL
```bash
sudo apt install gcc-avr avr-libc simavr libsimavr-dev libelf-dev gcc curl   # one time

python simulator/verify_firmware.py          # automatic check: measures Pin 13 / Pin 12 against the firmware spec

# Full system against the emulated chip:
simulator/run_emulator.sh 7777               # terminal 1: emulator, UART on tcp://127.0.0.1:7777
python run_dashboard.py --hitl-port socket://127.0.0.1:7777     # terminal 2
```
`simulator/build/pins.log` records every Pin 13 / Pin 12 edge with a timestamp (`P13 <seconds> <0|1>`).

## Option B — Wokwi (browser-style simulator with a visual board)
1. Build the firmware: `simulator/build_firmware.sh` (or export the compiled `.hex` from the Arduino IDE / `arduino-cli`
   and point `wokwi/wokwi.toml` at it).
2. Open the `simulator/wokwi` folder in VS Code with the **Wokwi Simulator** extension → *Wokwi: Start Simulator*.
3. `python run_dashboard.py --hitl-port rfc2217://localhost:4000`

> The Wokwi files (`wokwi.toml`, `diagram.json`) were written from Wokwi's documented format but could not be run in the
> environment where this was prepared (no access to Wokwi). Option A is the one that has been executed and verified.

## What was verified (Option A)
| Scenario | Packet | Measured Pin 13 | Pin 12 |
|---|---|---|---|
| Nominal | `<0,0,0>` | LOW | LOW |
| Elevated | `<1,1,1>` | steady HIGH | HIGH |
| Load shedding | `<1,2,2>` | 249.9 ms half-period | HIGH (held, firmware does not touch it) |
| Safe mode | `<1,3,3>` | steady HIGH | HIGH |
| Safety override | `<1,4,2>` | 50.2 ms half-period | HIGH |

Note: the dashboard's LED widget shows the mode derived from the chip's ACK (`HITLProtocol.derive_actuation`);
`verify_firmware.py` proves that derivation matches what the real firmware does on the pins.


## Live simulator monitor (HTML + Python backend)

The page `docs/arduino_hitl_simulator.html` is now a **monitor/control UI**, not a local firmware animation. Open it through the running FastAPI app at `http://127.0.0.1:8000/arduino-simulator`; its commands go to `/api/simulator/command` and status is polled from `/api/simulator/status`. Do not open the HTML with `file://`, because the backend API will not be available from that origin.

### Windows 10/11 setup using WSL2 (simavr, actual sketch)

1. Install WSL2 + Ubuntu from an Administrator PowerShell:
   ```powershell
   wsl --install -d Ubuntu
   ```
   Restart if Windows asks, then open Ubuntu.
2. In Ubuntu, install the AVR compiler and emulator:
   ```bash
   sudo apt update
   sudo apt install -y gcc-avr avr-libc simavr libsimavr-dev libelf-dev gcc make curl python3-venv
   ```
3. Navigate to the project directory as mounted under `/mnt/c/...` (or clone/copy it into your Ubuntu home), then build and verify the actual `.ino` firmware:
   ```bash
   chmod +x simulator/build_firmware.sh simulator/run_emulator.sh
   python3 simulator/verify_firmware.py
   ```
4. Terminal 1 — start the emulated ATmega328P running the compiled firmware:
   ```bash
   simulator/run_emulator.sh 7777
   ```
5. Terminal 2 — install Python dependencies and start the dashboard against the emulator:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python run_dashboard.py --hitl-port socket://127.0.0.1:7777
   ```
6. Open `http://127.0.0.1:8000/arduino-simulator`. Try the scenarios and watch Pin 13 / Pin 12 update. With simavr, the status endpoint reads the actual MCU pin-edge log at `simulator/build/pins.log`. Manual UI commands hold control for five seconds so the automatic telemetry stream does not immediately overwrite the test command.

The firmware build/emulator requires Linux/WSL tools; the browser page alone is not a substitute for the emulated MCU. If you prefer a visual circuit board, use the Wokwi VS Code extension with `simulator/wokwi`; that path depends on the extension and its RFC2217 serial bridge and should be verified on your machine.
