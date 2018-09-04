#!/usr/bin/env python

import sys
import os
from subprocess import run, PIPE
import re
from collections import namedtuple

Sink = namedtuple("Sink", ["id", "name", "volume", "muted"])


def get_sinks():
    """Get sinks, and default sink index."""
    sink_ids = []
    sink_names = []
    sink_volumes = []
    sink_muted = []
    default_sink_index = 0

    pacmd_output = run(["pacmd", "list-sinks"], stdout=PIPE)
    i = 0
    for line in pacmd_output.stdout.decode("utf8").splitlines():
        m = re.match("^  ( |\*) index: (\d+)$", line)
        if m:
            sink_ids.append(m.group(2))
            if m.group(1) == "*":
                default_sink_index = i
            i += 1
            continue
        m = re.match('\s+alsa.card_name = "([^"]+)"', line)
        if m:
            sink_names.append(m.group(1))
            continue
        m = re.match('\s+volume:\s+[\w-]+:\s+\d+\s+/\s+(\d+)%', line)
        if m:
            sink_volumes.append(m.group(1))
            continue
        m = re.match('\s+muted:\s+(\w+)', line)
        if m:
            sink_muted.append(True if m.group(1) == "yes" else False)
            continue

    sinks = [Sink(*props) for props in
             zip(sink_ids, sink_names, sink_volumes, sink_muted)]
    return sinks, default_sink_index


def change_sink(sinks, n):
    """Set sink n to default and move all inputs to sink n."""
    sys.stderr.write(f"Changing to sink {sinks[n]}...\n")

    run(["pacmd", "set-default-sink", sinks[n].id])

    pacmd_output = run(["pacmd", "list-sink-inputs"], stdout=PIPE)
    for line in pacmd_output.stdout.decode("utf8").splitlines():
        m = re.match("^    index: (\d+)$", line)
        if m:
            input_id = m.group(1)
            sys.stderr.write(f"Moving input {input_id}...\n")
            run(["pacmd", "move-sink-input", input_id, sinks[n].id])


def mute_default_sink():
    sys.stderr.write("Muting default sink...\n")
    run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])


def set_default_sink_volume(amount):
    sys.stderr.write(f"Setting default sink volume {amount}...")
    run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", amount])


def main():
    sinks, default_sink_index = get_sinks()

    button = os.environ.get("BLOCK_BUTTON")
    if button == "1":
        # left click: set sink
        next_default_index = (default_sink_index + 1)%len(sinks)
        change_sink(sinks, next_default_index)
    elif button == "2":
        # middle click: set to 100%
        set_default_sink_volume("100%")
    elif button == "3":
        # right click: mute
        mute_default_sink()
    elif button == "4":
        # scroll up: raise volume
        set_default_sink_volume("+2000")
    elif button == "5":
        # scroll down: lower volume
        set_default_sink_volume("-2000")

    if button is not None:
        sinks, default_sink_index = get_sinks()

    short_name = sinks[default_sink_index].name[0]
    name = sinks[default_sink_index].name
    if sinks[default_sink_index].muted:
        volume = "----"
    else:
        volume = "{:>3s}%".format(sinks[default_sink_index].volume)

    print(f"{short_name} {volume}")
    print(f"{name} {volume}")


if __name__ == '__main__':
    main()
