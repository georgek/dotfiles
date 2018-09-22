#!/usr/bin/env python

import sys
import time
from collections import deque

BLOCKS = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
COLOURS = [
    "#7F9F7F",           # green
    "#F0DFAF",           # yellow
    "#DFAF8F",           # orange
    "#CC9393",           # red
]
GRAPHSIZE = 15


def getstat():
    """Returns tuple containing active time and total time."""
    with open("/proc/stat") as stat:
        line = next(stat)
        times = [int(n) for n in line.split()[1:]]
        total = sum(times)
        active = total - times[3] - times[4]
    return active, total


def render_history(history):
    """Returns rendered graph."""
    blks = len(BLOCKS)-1
    cols = len(COLOURS)-1
    blockns = [int(frac*blks) for frac in history]
    colourns = [round(frac*cols) for frac in history]
    return "".join(f'<span foreground="{COLOURS[n]}">{BLOCKS[m]}</span>'
                   for m, n in zip(blockns, colourns))


def main():
    history = deque([0]*GRAPHSIZE, maxlen=GRAPHSIZE)
    graph = render_history(history)
    out = f'{graph}---%\n'
    sys.stdout.write(out)
    sys.stdout.flush()

    while True:
        active1, total1 = getstat()
        time.sleep(2)
        active2, total2 = getstat()
        frac = (active2-active1)/(total2-total1)
        history.append(frac)
        graph = render_history(history)
        colour = COLOURS[round(frac*(len(COLOURS)-1))]
        out = f'{graph}<span foreground="{colour}">{frac*100:3.0f}%</span>\n'
        sys.stdout.write(out)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
