#!/usr/bin/env python

import subprocess
import sys
import time

SLEEP_TIME = 1


def get_frequencies():
    process = subprocess.run(
        ["grep", "--color=never", "cpu MHz", "/proc/cpuinfo"], capture_output=True
    )
    output = process.stdout.decode("utf8").strip()

    frequencies = [
        float(line.split()[-1]) for line in output.splitlines()
    ]
    return frequencies


def format_frequency(frequency):
    if frequency >= 1000:
        frequency /= 1000
        return f"{frequency:1.1f}GHz"
    else:
        return f"{frequency:>3.0f}MHz"


def main():
    while True:
        frequencies = get_frequencies()
        out = " ".join(format_frequency(frequency) for frequency in frequencies)
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
