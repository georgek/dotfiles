#!/usr/bin/env python

import sys
import os
from subprocess import run, PIPE
import re


def get_sinks():
    """Get sinks, sink names, and default sink index."""
    sinks = []
    sink_names = []
    default_sink_index = 0

    pacmd_output = run(["pacmd", "list-sinks"], stdout=PIPE)
    i = 0
    for line in pacmd_output.stdout.decode("utf8").splitlines():
        m = re.match("^  ( |\*) index: (\d+)$", line)
        if m:
            sinks.append(m.group(2))
            if m.group(1) == "*":
                default_sink_index = i
            i += 1
            continue
        m = re.match('\s+alsa.card_name = "([^"]+)"', line)
        if m:
            sink_names.append(m.group(1))

    return sinks, sink_names, default_sink_index


def change_sink(sinks, n):
    """Set sink n to default and move all inputs to sink n."""
    sys.stderr.write(f"Changing to sink {sinks[n]}...\n")

    run(["pacmd", "set-default-sink", sinks[n]])

    pacmd_output = run(["pacmd", "list-sink-inputs"], stdout=PIPE)
    for line in pacmd_output.stdout.decode("utf8").splitlines():
        m = re.match("^    index: (\d+)$", line)
        if m:
            input_id = m.group(1)
            sys.stderr.write(f"Moving input {input_id}...\n")
            run(["pacmd", "move-sink-input", input_id, sinks[n]])


def main():
    sinks, sink_names, default_sink_index = get_sinks()

    if os.environ.get("BLOCK_BUTTON"):
        next_default_index = (default_sink_index + 1)%len(sinks)
        change_sink(sinks, next_default_index)
        default_sink_index = next_default_index

    print(sink_names[default_sink_index][0])  # short
    print(sink_names[default_sink_index])     # long


if __name__ == '__main__':
    main()
