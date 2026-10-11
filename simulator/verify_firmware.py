"""
Automated check: Python HITL bridge  ->  REAL firmware on an emulated ATmega328P  ->  measured pin waveforms.

Run from the project root:   python simulator/verify_firmware.py
Starts the emulator itself (simulator/run_emulator.sh), sends one packet per scenario through the same
HITLSerialBridge the dashboard uses, then compares the *measured* Pin 13 / Pin 12 behaviour with the
firmware spec (50 ms strobe, 250 ms pulse, relay rules).
"""
import os, sys, time, subprocess, statistics
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.hitl.serial_bridge import HITLSerialBridge

PORT, PINLOG = 7791, os.path.join(ROOT, "simulator", "build", "pins.log")
HOLD = 1.6  # seconds per scenario
# name, alert, severity, rl, expected P13 half-period ms (None = steady), expected P13 steady level, expected P12 level
SCENARIOS = [
    ("Nominal",            0, "NORMAL",    0, None, 0, 0),
    ("Elevated / pre-arm", 1, "ELEVATED",  1, None, 1, 1),
    ("Load shedding",      1, "WARNING",   2, 250,  None, 1),   # relay holds previous HIGH (firmware quirk)
    ("Safe mode",          1, "CRITICAL",  3, None, 1, 1),
    ("Safety override",    1, "EMERGENCY", 2, 50,   None, 1),
    ("Back to nominal",    0, "NORMAL",    0, None, 0, 0),
]

def wait_port(port, timeout=30.0):
    import socket
    end = time.time() + timeout
    while time.time() < end:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
            return True
        except OSError:
            time.sleep(0.3)
    return False

def main():
    if not os.path.exists(os.path.join(ROOT, "simulator", "build", "firmware.elf")):
        print("[*] Building firmware (first run downloads the Arduino core)...")
        subprocess.run([os.path.join(ROOT, "simulator", "build_firmware.sh")], check=True, stdout=subprocess.DEVNULL)
    emu = subprocess.Popen([os.path.join(ROOT, "simulator", "run_emulator.sh"), str(PORT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_port(PORT):
            sys.exit("FAIL: emulator did not start (are simavr, libsimavr-dev, libelf-dev, gcc installed?)")
        bridge = HITLSerialBridge(port=f"socket://127.0.0.1:{PORT}", auto_fallback_virtual=False)
        if bridge.is_virtual or bridge.serial_conn is None:
            sys.exit("FAIL: bridge could not reach the emulator")
        time.sleep(1.2)  # boot flashes
        acks = []
        for name, alert, sev, rl, *_ in SCENARIOS:
            info = bridge.send_anomaly_alert(alert, sev, rl)
            ack = info["last_ack"]
            acks.append(int(ack.strip("<>").split(",")[-1]))   # firmware millis() at ACK time
            time.sleep(HOLD)
        bridge.close()
    finally:
        emu.terminate(); emu.wait()

    ev = [(l.split()[0], float(l.split()[1]) * 1000, int(l.split()[2])) for l in open(PINLOG)]
    lvl = lambda pin, t: [v for p, ts, v in ev if p == pin and ts <= t][-1:] or [0]
    ok = True
    print(f"{'scenario':20} {'P13 half-period':>16} {'P13 level':>10} {'P12':>5}  result")
    for i, (name, alert, sev, rl, hp_exp, p13_exp, p12_exp) in enumerate(SCENARIOS):
        a = acks[i]; z = acks[i + 1] if i + 1 < len(acks) else a + HOLD * 1000
        edges = [ts for p, ts, v in ev if p == "P13" and a <= ts < z]
        gaps = [edges[j + 1] - edges[j] for j in range(len(edges) - 1)]
        hp = statistics.median(gaps) if len(gaps) >= 3 else None
        p13 = lvl("P13", z - 1)[0]; p12 = lvl("P12", z - 1)[0]
        good = (p12 == p12_exp) and ((hp_exp is None and hp is None and p13 == p13_exp) or
                                      (hp_exp is not None and hp is not None and abs(hp - hp_exp) <= 5))
        ok &= good
        print(f"{name:20} {('%.1f ms' % hp) if hp else 'steady':>16} {'-' if hp else ('HIGH' if p13 else 'LOW'):>10} "
              f"{'HIGH' if p12 else 'LOW':>5}  {'PASS' if good else 'FAIL'}")
    print("\nALL SCENARIOS MATCH THE REAL FIRMWARE" if ok else "\nMISMATCH FOUND")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
