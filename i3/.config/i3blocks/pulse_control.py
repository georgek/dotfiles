#!/usr/bin/env python
"""
Display and control pulseaudio settings using i3blocks
"""

import sys
import os
from subprocess import run, PIPE
import re
from collections import namedtuple

YELLOW = "#F0DFAF"
RED = "#CC9393"

Sink = namedtuple("Sink", ["id", "name", "volume", "muted"])


def with_colour(string, colour):
    """Returns string with pango colour"""
    return f'<span foreground="{colour}">{string}</span>'


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
        match = re.match(r"^  ( |\*) index: (\d+)$", line)
        if match:
            sink_ids.append(match.group(2))
            if match.group(1) == "*":
                default_sink_index = i
            i += 1
            continue
        match = re.match(r'\s+alsa.card_name = "([^"]+)"', line)
        if match:
            sink_names.append(match.group(1))
            continue
        match = re.match(r'\s+volume:\s+[\w-]+:\s+\d+\s+/\s+(\d+)%', line)
        if match:
            sink_volumes.append(int(match.group(1)))
            continue
        match = re.match(r'\s+muted:\s+(\w+)', line)
        if match:
            sink_muted.append(True if match.group(1) == "yes" else False)
            continue

    sinks = [Sink(*props) for props in
             zip(sink_ids, sink_names, sink_volumes, sink_muted)]
    return sinks, default_sink_index


def change_sink(sinks, sink_index):
    """Set sink sink_index to default and move all inputs to sink sink_index.

    """
    sys.stderr.write(f"Changing to sink {sinks[sink_index]}...\n")

    run(["pacmd", "set-default-sink", sinks[sink_index].id])

    pacmd_output = run(["pacmd", "list-sink-inputs"], stdout=PIPE)
    for line in pacmd_output.stdout.decode("utf8").splitlines():
        match = re.match(r"^    index: (\d+)$", line)
        if match:
            input_id = match.group(1)
            sys.stderr.write(f"Moving input {input_id}...\n")
            run(["pacmd", "move-sink-input", input_id, sinks[sink_index].id])


def mute_default_sink():
    """Mute the default sink"""
    sys.stderr.write("Muting default sink...\n")
    run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])


def set_default_sink_volume(amount):
    """Set default sink volume to amount"""
    sys.stderr.write(f"Setting default sink volume {amount}...")
    run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", amount])


def main():
    """Entry point to program"""
    sinks, default_sink_index = get_sinks()

    button = os.environ.get("BLOCK_BUTTON")
    if button == "1":
        # left click: set sink
        next_default_index = (default_sink_index + 1) % len(sinks)
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

    volume = sinks[default_sink_index].volume

    # short_name = sinks[default_sink_index].name.split()[0]
    name = sinks[default_sink_index].name
    if sinks[default_sink_index].muted:
        volume_str = f"{volume:>3d}~"
    else:
        volume_str = f"{volume:>3d}%"

    if volume > 100:
        volume_str = with_colour(volume_str, RED)

    out_str = f"{name} {volume_str}"
    if sinks[default_sink_index].muted:
        out_str = with_colour(out_str, YELLOW)

    sys.stdout.write(out_str)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
