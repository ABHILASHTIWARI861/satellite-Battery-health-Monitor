"""
PySerial Hardware-in-the-Loop Bridge
Connects Python runtime to physical Arduino UNO over USB Serial.
Automatically discovers ports, handles timeouts, and falls back to Virtual Arduino Emulator.
"""

import time
import os
from typing import Dict, Any, Optional, List
from .protocol import HITLProtocol
from .virtual_arduino import VirtualArduino

try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False


def get_wsl_host_ip() -> Optional[str]:
    """Detects Windows host IP when running inside WSL2 environment."""
    try:
        with open("/proc/net/route", "r") as f:
            for line in f.readlines()[1:]:
                fields = line.strip().split()
                if fields[1] == "00000000":  # default route
                    import socket, struct
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
    except Exception:
        pass
    return None


class HITLSerialBridge:
    """
    Manages physical / virtual serial connection to Arduino UNO.
    Transmits alert states to drive Digital Pin 13 (Built-in LED) and receives status telemetry.
    """

    def __init__(
        self,
        port: str = "AUTO",
        baud_rate: int = 115200,
        timeout: float = 0.5,
        auto_fallback_virtual: bool = True
    ):
        self.port_setting = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.auto_fallback_virtual = auto_fallback_virtual

        self.serial_conn = None
        self.virtual_device: Optional[VirtualArduino] = None
        self.is_virtual = False
        self.active_port_name = "NONE"
        self.last_sent_alert = 0
        self.last_sent_severity = "NORMAL"
        self.last_sent_rl_action = 0
        self.last_relay = 0
        # Monotonic deadline while the simulator UI has temporary manual control.
        self.manual_override_until = 0.0

        self.connect()

    def discover_ports(self) -> List[str]:
        """Scans system for available serial ports with Arduino/USB descriptions"""
        if not HAS_PYSERIAL:
            return []
        try:
            matched_ports = []
            for p in serial.tools.list_ports.comports():
                desc = (p.description or "").lower()
                mfg = (p.manufacturer or "").lower()
                # Prioritize devices matching microcontroller/USB signatures
                if any(kw in desc or kw in mfg for kw in ["arduino", "ch340", "cp210", "ftdi", "usb serial", "ch341"]):
                    matched_ports.insert(0, p.device)
                else:
                    matched_ports.append(p.device)
            return matched_ports
        except Exception:
            return []

    def connect(self) -> bool:
        """Attempts connection to physical serial port, or initializes virtual emulator"""
        if self.port_setting.upper() != "VIRTUAL" and HAS_PYSERIAL:
            ports = self.discover_ports() if self.port_setting.upper() == "AUTO" else [self.port_setting]
            
            # If running in WSL and target is localhost/127.0.0.1, also try Windows host gateway IP
            wsl_host = get_wsl_host_ip()
            candidate_ports = []
            for p in ports:
                candidate_ports.append(p)
                if wsl_host:
                    if "localhost" in p:
                        candidate_ports.append(p.replace("localhost", wsl_host))
                    elif "127.0.0.1" in p:
                        candidate_ports.append(p.replace("127.0.0.1", wsl_host))

            for p in candidate_ports:
                try:
                    # serial_for_url accepts plain ports ('COM3', '/dev/ttyACM0') AND URLs such as
                    # 'rfc2217://localhost:4000' (Wokwi) or 'socket://127.0.0.1:7777' (simavr emulator).
                    # NOTE: PySerial's rfc2217 implementation raises NotImplementedError if write_timeout is given!
                    kwargs = {"baudrate": self.baud_rate, "timeout": self.timeout}
                    if not p.lower().startswith("rfc2217://"):
                        kwargs["write_timeout"] = self.timeout

                    conn = serial.serial_for_url(p, **kwargs)
                    time.sleep(0.5)  # Allow Arduino reset on DTR toggle
                    self.serial_conn = conn
                    self.is_virtual = False
                    self.active_port_name = p
                    self.virtual_device = None
                    print(f"[*] HITL Hardware Bridge connected to Arduino/emulator on {p} @ {self.baud_rate} baud")
                    return True
                except Exception as e:
                    if self.port_setting.upper() != "AUTO":
                        print(f"[!] Failed to connect to port/URL '{p}': {e}")
                    continue

        if self.auto_fallback_virtual or not HAS_PYSERIAL:
            print("[*] Falling back to Virtual Arduino emulator.")
            self.virtual_device = VirtualArduino(port_name="VIRTUAL_COM_UNO")
            self.is_virtual = True
            self.active_port_name = "VIRTUAL_COM_UNO"
            self.serial_conn = None
            return True

        return False

    def send_anomaly_alert(
        self,
        alert_state: int,
        severity: str = "NORMAL",
        rl_action: int = 0
    ) -> Dict[str, Any]:
        """
        Sends binary and ASCII command to Arduino to drive Pin 13 LED.
        alert_state: 0 (Normal / LED OFF), 1 (Anomaly Alert / LED ON)
        severity: "NORMAL", "ELEVATED", "WARNING", "CRITICAL", "OVERRIDE"
        """
        self.last_sent_alert = int(alert_state)
        self.last_sent_severity = severity
        self.last_sent_rl_action = int(rl_action)

        # Encode formatted ASCII packet: <ALERT,SEV,RL>
        ascii_pkt = HITLProtocol.encode_ascii_line(alert_state, severity, rl_action)
        pkt_bytes = ascii_pkt.encode("utf-8")

        response_info = {}

        if self.is_virtual and self.virtual_device:
            self.virtual_device.write(pkt_bytes)
            ack = self.virtual_device.readline()
            response_info = self.virtual_device.get_hardware_status()
        elif self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(pkt_bytes)
                self.serial_conn.flush()
                raw_ack = self.serial_conn.readline().decode("utf-8", errors="ignore")
                parsed = HITLProtocol.decode_ascii_line(raw_ack)
                sev_code = parsed["ack_severity"] if parsed else HITLProtocol.SEVERITY_MAP.get(severity.upper(), 0)
                act = HITLProtocol.derive_actuation(self.last_sent_alert, sev_code, rl_action, self.last_relay)
                self.last_relay = act["relay"]
                device_label = "Arduino Uno (Physical Hardware)"
                if "rfc2217" in str(self.active_port_name).lower():
                    device_label = "Arduino Uno (Wokwi Simulator)"
                elif "socket://" in str(self.active_port_name).lower():
                    device_label = "Arduino Uno (simavr Emulator)"

                response_info = {
                    "device": device_label,
                    "port": self.active_port_name,
                    "connected": True,
                    "pin13_led_state": self.last_sent_alert,
                    "pin13_mode": act["mode"],
                    "pin12_relay_state": act["relay"],
                    "blink_ms": act["blink_ms"],
                    "is_virtual": False,
                    "last_tx": ascii_pkt.strip(),
                    "last_ack": raw_ack.strip(),
                    "active_severity": severity,
                    "active_rl_action": rl_action,
                    "raw_ack": raw_ack.strip(),
                    "parsed_ack": parsed
                }
            except Exception as e:
                print(f"[!] Serial write error: {e}. Switching to virtual emulator.")
                self.is_virtual = True
                self.virtual_device = VirtualArduino(port_name="VIRTUAL_COM_UNO")
                if self.serial_conn:
                    try:
                        self.serial_conn.close()
                    except Exception:
                        pass
                self.serial_conn = None

        return response_info

    def get_status(self) -> Dict[str, Any]:
        """Returns current bridge status"""
        if self.is_virtual and self.virtual_device:
            return self.virtual_device.get_hardware_status()
        sev_code = HITLProtocol.SEVERITY_MAP.get(self.last_sent_severity.upper(), 0)
        act = HITLProtocol.derive_actuation(
            self.last_sent_alert, sev_code, self.last_sent_rl_action, self.last_relay
        )
        device_label = "Arduino Uno (Physical Hardware)"
        if "rfc2217" in str(self.active_port_name).lower():
            device_label = "Arduino Uno (Wokwi Simulator)"
        elif "socket://" in str(self.active_port_name).lower():
            device_label = "Arduino Uno (simavr Emulator)"

        return {
            "device": device_label,
            "port": self.active_port_name,
            "connected": self.serial_conn is not None and self.serial_conn.is_open,
            "pin13_led_state": act["pin13"],
            "pin13_mode": act["mode"],
            "pin12_relay_state": act["relay"],
            "blink_ms": act["blink_ms"],
            "active_severity": self.last_sent_severity,
            "active_rl_action": self.last_sent_rl_action,
            "last_sent_alert": self.last_sent_alert,
            "is_virtual": self.is_virtual
        }

    def close(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        if self.virtual_device:
            self.virtual_device.close()
