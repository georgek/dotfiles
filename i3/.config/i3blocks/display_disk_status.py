#!/usr/bin/env python3.7

import sys

DISK_STATUS_FILE_NAME = "/tmp/disk_status"
DISK_USAGE_FILE_NAME = "/tmp/disk_usage"

BLOCKS = ("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█")
COLOURS = (
    "#7F9F7F",           # green
    "#F0DFAF",           # yellow
    "#DFAF8F",           # orange
    "#CC9393",           # red
)

SSDS = (
    "sda",
    "sdd",
)


def little_status(status):
    if status == "UP":
        return "u"
    elif status == "ASLEEP":
        return "z"
    else:
        return "?"


def make_block(amount):
    blks = len(BLOCKS)-1
    cols = len(COLOURS)-1
    blockn = int(amount*blks)
    colourn = round(amount*cols)
    return f'<span foreground="{COLOURS[colourn]}">{BLOCKS[blockn]}</span>'


def main():
    try:
        with open(DISK_STATUS_FILE_NAME) as disk_status_file:
            disk_status_dict = dict(line.split() for line in disk_status_file)
    except FileNotFoundError:
        disk_status_dict = {}

    try:
        with open(DISK_USAGE_FILE_NAME) as disk_usage_file:
            items = (line.split() for line in disk_usage_file)
            disk_usage_dict = dict((item[0], item[4]) for item in items)
    except FileNotFoundError:
        disk_usage_dict = {}

    info = []
    for disk, status in disk_status_dict.items():
        usage = disk_usage_dict.get(disk, "100%")
        usage = int(usage[:-1])/100
        block = make_block(usage)
        if disk in SSDS:
            info.append(f"{block} {disk}(s)")
        else:
            info.append(f"{block} {disk}({little_status(status)})")

    out = " ".join(info)
    sys.stdout.write(out)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
