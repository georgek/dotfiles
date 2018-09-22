#!/usr/bin/env python
"""
Display htop-style memory usage
"""

from collections import namedtuple
from math import ceil

GRAPH_WIDTH = 20

Usage = namedtuple("Usage", ["memtotal", "active", "buffers", "cache",
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

    with open("/proc/meminfo") as f:
        for line in f:
            split = line.split()
            name = split[0]
            amount = int(split[1])
            if name == "MemTotal:":
                memtotal = amount
            elif name == "Active:":
                active = amount
            elif name == "Buffers:":
                buffers = amount
            elif name == "Cached:":
                cache = amount
            elif name == "SwapTotal:":
                swaptotal = amount
            elif name == "SwapFree:":
                swapfree = amount

    return Usage(memtotal, active, buffers, cache, swaptotal, swapfree)


def make_mem_graph(usage: Usage, graph_width: int = GRAPH_WIDTH) -> str:
    """Make memory graph at desired width"""

    width_each = graph_width - 2
    active = ceil(usage.active
                  / usage.memtotal*width_each)
    buffers = ceil(usage.buffers
                   / usage.memtotal*width_each)
    cached = ceil(usage.cache
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

    active_gib = usage.active/1024/1024
    active_str = f"{active_gib:2.1f}"
    active_proportion = usage.active/usage.memtotal

    if active_proportion >= 0.9:
        active_str = with_colour(active_str, RED)
    elif active_proportion >= 0.7:
        active_str = with_colour(active_str, ORANGE)
    elif active_proportion >= 0.5:
        active_str = with_colour(active_str, YELLOW)

    return f"[{bars}{active_str}G]"


def make_swap_graph(usage: Usage) -> str:
    """Make swap graph"""
    swap_usage = usage.swaptotal - usage.swapfree
    swap_gib = swap_usage/1024/1024
    swap_str = f"{swap_gib:1.1f}"
    swap_proportion = swap_usage/usage.swaptotal

    if swap_proportion > 0:
        swap_str = with_colour(swap_str, RED)

    return f"[{swap_str}G]"


def main():
    usage = get_usage()

    mem_label = "Mem"
    mem_graph = make_mem_graph(usage)

    swap_label = "Swp"
    swap_graph = make_swap_graph(usage)

    print(f"{mem_label}{mem_graph} {swap_label}{swap_graph}")


if __name__ == '__main__':
    main()
