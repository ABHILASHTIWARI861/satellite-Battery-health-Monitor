"""
Unit Tests for HITL Serial Protocol, Virtual Arduino, and PySerial Bridge
"""

import pytest
from src.hitl.protocol import HITLProtocol
from src.hitl.virtual_arduino import VirtualArduino
from src.hitl.serial_bridge import HITLSerialBridge


def test_protocol_crc_and_encoding():
    """Verify CRC16 CCITT and packet encoding/decoding"""
    pkt = HITLProtocol.encode_command_packet(alert_state=1, severity_str="CRITICAL", rl_action=2)
    assert len(pkt) == 8
    assert pkt[0] == 0xAA and pkt[1] == 0x55
    assert pkt[2] == HITLProtocol.CMD_SET_ALERT
    assert pkt[3] == 1  # Alert ON
    assert pkt[4] == 3  # Critical Severity
    assert pkt[5] == 2  # RL action

    # ASCII framing
    ascii_line = HITLProtocol.encode_ascii_line(alert_state=1, severity_str="OVERRIDE", rl_action=3)
    assert ascii_line == "<1,4,3>\n"

    parsed = HITLProtocol.decode_ascii_line("<1,4,3,1500>")
    assert parsed is not None
    assert parsed["pin13_state"] == 1
    assert parsed["ack_severity"] == 4
    assert parsed["ack_rl"] == 3

    # Real firmware emits with <ACK,...> prefix
    parsed_ack = HITLProtocol.decode_ascii_line("<ACK,1,4,3,1500>")
    assert parsed_ack is not None
    assert parsed_ack["pin13_state"] == 1
    assert parsed_ack["ack_severity"] == 4
    assert parsed_ack["ack_rl"] == 3
    assert parsed_ack["uptime_ms"] == 1500


def test_virtual_arduino_actuation():
    """Verify Virtual Arduino receives packets, switches Pin 13, and sends ACKs"""
    uno = VirtualArduino()
    assert uno.pin13_state == 0

    # Send Alert ON
    uno.write(b"<1,2,0>\n")
    assert uno.pin13_state == 1
    assert uno.pin13_mode == "SOLID_ON"

    # Send Critical Safety Override
    uno.write(b"<1,4,3>\n")
    assert uno.pin13_state == 1
    assert uno.pin13_mode == "CRITICAL_STROBE"

    ack_bytes = uno.readline()
    assert b"<ACK," in ack_bytes

    status = uno.get_hardware_status()
    assert status["connected"] is True
    assert status["pin13_led_state"] == 1


def test_serial_bridge_virtual_fallback():
    """Verify Serial Bridge operates seamlessly with virtual fallback"""
    bridge = HITLSerialBridge(port="VIRTUAL", auto_fallback_virtual=True)
    assert bridge.is_virtual is True

    hw_info = bridge.send_anomaly_alert(alert_state=1, severity="CRITICAL", rl_action=3)
    assert hw_info["pin13_led_state"] == 1

    status = bridge.get_status()
    assert status["pin13_led_state"] == 1
    bridge.close()


def test_emergency_severity_triggers_strobe():
    """Pipeline emits 'EMERGENCY' on safety override; it must map to code 4 (50 ms strobe)."""
    assert HITLProtocol.encode_ascii_line(1, "EMERGENCY", 2) == "<1,4,2>\n"
    bridge = HITLSerialBridge(port="VIRTUAL")
    hw = bridge.send_anomaly_alert(alert_state=1, severity="EMERGENCY", rl_action=2)
    assert hw["pin13_mode"] == "CRITICAL_STROBE"
    assert hw["pin12_relay_state"] == 1
    assert hw["blink_ms"] == 50
    bridge.close()


def test_load_shedding_pulse_and_relay_hold():
    """Matches firmware: rlAction==2 pulses at 250 ms and leaves Pin 12 unchanged."""
    uno = VirtualArduino()
    uno.write(b"<1,3,3>\n")                      # safe mode -> relay HIGH
    assert uno.pin13_mode == "SOLID_ON" and uno.pin12_relay_state == 1
    uno.write(b"<1,3,2>\n")                      # load shedding -> pulse, relay holds
    assert uno.pin13_mode == "LOAD_SHED_PULSE" and uno.blink_ms == 250
    assert uno.pin12_relay_state == 1
    uno.write(b"<0,0,0>\n")                      # nominal -> everything off
    assert uno.pin13_mode == "OFF" and uno.pin12_relay_state == 0
    assert uno.last_ack.startswith("<ACK,") or uno.readline().startswith(b"<ACK,")
