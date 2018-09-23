#!/usr/bin/env python
"""
Display htop-style memory usage
"""

from collections import namedtuple
from math import ceil
import sys
from time import sleep

GRAPH_WIDTH = 20
SLEEP_TIME = 10

Usage = namedtuple("Usage", ["memtotal", "active", "buffers", "cached",
                             "swaptotal", "swapfree"])

GREY = "#656555"
GREEN = "#7F9F7F"
BLUE = "#8CD0D3"
YELLOW = "#F0DFAF"
ORANGE = "#DFAF8F"
RED = "#CC9393"


def with_colour(string, colour):
    """Returns string with pango colour"""
    return f'<span foreground="{colour}">{string}</span>'


def get_usage():
    """Get memory usage from /proc/meminfo"""

    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            split = line.split()
            name = split[0][:-1]
            meminfo[name] = int(split[1])

    memtotal = meminfo["MemTotal"]
    usedtotal = memtotal - meminfo["MemFree"]
    buffers = meminfo["Buffers"]
    cached = meminfo["Cached"] + meminfo["SReclaimable"] - meminfo["Shmem"]
    active = usedtotal - buffers - cached

    swaptotal = meminfo["SwapTotal"]
    swapfree = meminfo["SwapFree"]

    return Usage(memtotal, active, buffers, cached, swaptotal, swapfree)


def mem_graph(usage: Usage, graph_width: int = GRAPH_WIDTH) -> str:
    """Make memory graph at desired width"""

    width_each = graph_width - 2
    active = ceil(usage.active
                  / usage.memtotal*width_each)
    buffers = ceil(usage.buffers
                   / usage.memtotal*width_each)
    cached = ceil(usage.cached
                  / usage.memtotal*width_each)
    total = active + buffers + cached

    active_bars = with_colour("|" * active, GREEN)
    buffers_bars = with_colour("|" * buffers, BLUE)
    cached_bars = with_colour("|" * cached, YELLOW)

    bars = "".join([
        active_bars,
        buffers_bars,
        cached_bars,
        " " * (graph_width - total),
    ])

    return bars


def mem_amount(usage: Usage) -> str:
    active_gib = usage.active/1024/1024
    active_str = f"{active_gib:2.1f}G"
    active_proportion = usage.active/usage.memtotal

    if active_proportion >= 0.9:
        active_str = with_colour(active_str, RED)
    elif active_proportion >= 0.7:
        active_str = with_colour(active_str, ORANGE)
    elif active_proportion >= 0.5:
        active_str = with_colour(active_str, YELLOW)
    else:
        active_str = with_colour(active_str, GREEN)

    return active_str


def swap_amount(usage: Usage) -> str:
    """Make swap graph"""
    swap_usage = usage.swaptotal - usage.swapfree
    swap_gib = swap_usage/1024/1024
    swap_str = f"{swap_gib:1.1f}G"
    swap_proportion = swap_usage/usage.swaptotal

    if swap_proportion > 0:
        swap_str = with_colour(swap_str, RED)
    else:
        swap_str = with_colour(swap_str, GREEN)

    return swap_str


def main():
    while True:
        usage = get_usage()

        mem_label = "Mem"
        mgraph = mem_graph(usage)
        mamount = mem_amount(usage)

        swap_label = "Swp"
        samount = swap_amount(usage)

        sys.stdout.write(       # short
            f"{mem_label}[{mamount}] {swap_label}[{samount}]\n",
        )
        sys.stdout.flush()
        sys.stdout.write(       # long
            f"{mem_label}[{mgraph}{mamount}] {swap_label}[{samount}]\n",
        )
        sys.stdout.flush()
        sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
