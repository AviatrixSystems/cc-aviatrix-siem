#!/usr/bin/env python3
"""Send test syslog events with updated timestamps to Cribl.Cloud for E2E validation."""

import re
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SAMPLE_FILE = Path(__file__).parent / "samples" / "aviatrix-syslog.log"
TARGET_HOST = "default.main.ruminant-jennings-pq7qxk9.cribl.cloud"
TARGET_PORT = 9514

def update_timestamps(line: str, now: datetime) -> str:
    """Replace all timestamp formats in a log line with current time."""
    epoch_now = int(now.timestamp())
    epoch_ns = int(now.timestamp() * 1e9)
    syslog_ts = now.strftime("%b %d %H:%M:%S")
    iso_ts = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
    iso_tz = now.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    slash_ts = now.strftime("%Y/%m/%d %H:%M:%S")

    # Syslog header with PRI: "<14>Feb 25 00:17:31"
    line = re.sub(
        r'^(<\d{1,3}>)[A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2}',
        lambda m: f"{m.group(1)}{syslog_ts}", line
    )
    # CMD format: "Feb 25 00:21:40 18.190.163.185 Feb 25 00:21:40"
    line = re.sub(
        r'^([A-Z][a-z]{2} \d{1,2}) \d{2}:\d{2}:\d{2}( \d+\.\d+\.\d+\.\d+ [A-Z][a-z]{2} \d{1,2}) \d{2}:\d{2}:\d{2}',
        lambda m: f"{syslog_ts}{m.group(2)} {syslog_ts[7:]}", line
    )
    # FQDN format without PRI: starts with "Feb 25 ..."
    line = re.sub(
        r'^(Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Jan) \d{1,2} \d{2}:\d{2}:\d{2}',
        syslog_ts, line
    )

    # avx-gw-state-sync prefix: "2026/02/25 00:17:39"
    line = re.sub(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', slash_ts, line)

    # timestamp= field: "timestamp=2026-02-25T00:18:25.462667"
    line = re.sub(
        r'timestamp=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+',
        f'timestamp={iso_ts}', line
    )

    # Suricata JSON timestamp: "timestamp":"2026-02-25T00:20:14.511678+0000"
    line = re.sub(
        r'"timestamp"\s*:\s*"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{4}"',
        f'"timestamp":"{iso_ts}+0000"', line
    )

    # Tunnel status ISO timestamp: "2026-02-25T00:21:58.939683+00:00"
    line = re.sub(
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{2}:\d{2}',
        iso_tz, line
    )

    # MITM JSON epoch timestamp: "timestamp":1771978819
    line = re.sub(
        r'"timestamp"\s*:\s*\d{10}(?!\d)',
        f'"timestamp":{epoch_now}', line
    )

    # session_start nanoseconds: "session_start":1771978819667138916
    line = re.sub(
        r'"session_start"\s*:\s*\d{16,19}',
        f'"session_start":{epoch_ns}', line
    )

    # CPU cores protobuf nanos/seconds
    line = re.sub(r'seconds:\d{10}', f'seconds:{epoch_now}', line)

    # Flow start timestamp in suricata JSON
    line = re.sub(
        r'"start"\s*:\s*"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{4}"',
        f'"start":"{iso_ts}+0000"', line
    )

    return line


def main():
    if not SAMPLE_FILE.exists():
        print(f"Error: {SAMPLE_FILE} not found", file=sys.stderr)
        sys.exit(1)

    lines = [l.strip() for l in SAMPLE_FILE.read_text().splitlines() if l.strip()]
    print(f"Loaded {len(lines)} sample events from {SAMPLE_FILE.name}")

    now = datetime.now(timezone.utc)
    updated = []
    for line in lines:
        updated.append(update_timestamps(line, now))

    # Send via TCP
    print(f"Connecting to {TARGET_HOST}:{TARGET_PORT} (TCP)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((TARGET_HOST, TARGET_PORT))
        print("Connected!")
    except Exception as e:
        print(f"TCP connection failed: {e}", file=sys.stderr)
        print("Falling back to UDP...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i, msg in enumerate(updated, 1):
            sock.sendto(msg.encode("utf-8"), (TARGET_HOST, TARGET_PORT))
            print(f"\rSent {i}/{len(updated)} via UDP", end="", flush=True)
            time.sleep(0.05)
        print(f"\nDone! Sent {len(updated)} events via UDP to {TARGET_HOST}:{TARGET_PORT}")
        sock.close()
        return

    try:
        for i, msg in enumerate(updated, 1):
            sock.sendall((msg + "\n").encode("utf-8"))
            print(f"\rSent {i}/{len(updated)} via TCP", end="", flush=True)
            time.sleep(0.05)
        print(f"\nDone! Sent {len(updated)} events via TCP to {TARGET_HOST}:{TARGET_PORT}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
