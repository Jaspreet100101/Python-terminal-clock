import math
import shutil
import sys
import time
from datetime import datetime

RESET, BOLD = "\033[0m", "\033[1m"
RED, CYAN, YELLOW, WHITE, DIM = "\033[91m", "\033[96m", "\033[93m", "\033[97m", "\033[2m"

# 3x5 block font
FONT = {
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", "  █", "  █", "  █"],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    ":": [" ", "█", " ", "█", " "],
}


def big_text(s):
    """Return 5 strings that draw s in the block font."""
    return [" ".join(FONT[ch][r] for ch in s) for r in range(5)]


def build_face(rx, ry, now, big):
    w, h = 2 * rx + 1, 2 * ry + 1
    cx, cy = rx, ry
    grid = [[(" ", "") for _ in range(w)] for _ in range(h)]

    def put(x, y, ch, color=""):
        if 0 <= x < w and 0 <= y < h:
            grid[y][x] = (ch, color)

    # Dial ticks
    for i in range(60):
        a = math.radians(i * 6 - 90)
        x = round(cx + rx * math.cos(a))
        y = round(cy + ry * math.sin(a))
        put(x, y, "●" if i % 5 == 0 else "·", WHITE if i % 5 == 0 else DIM)

    # All hands use the same thin dotted style; only color and length differ
    def hand(angle_deg, length, color):
        a = math.radians(angle_deg - 90)
        steps = int(max(rx, ry) * length * 2) + 1
        for s in range(1, steps + 1):
            t = s / steps * length
            put(round(cx + t * rx * math.cos(a)),
                round(cy + t * ry * math.sin(a)), "·", color)

    hand(((now.hour % 12) + now.minute / 60) * 30, 0.50, YELLOW)   # hour: short
    hand((now.minute + now.second / 60) * 6, 0.72, CYAN)           # minute: medium
    hand(now.second * 6, 0.85, RED)                                # second: long
    put(cx, cy, "◉", BOLD + WHITE)

    # Hour numbers (drawn last so they stay readable)
    for hr in range(1, 13):
        a = math.radians(hr * 30 - 90)
        if big:
            x = round(cx + (rx - 5) * math.cos(a))
            y = round(cy + (ry - 3) * math.sin(a))
            rows = big_text(str(hr))
            left = x - len(rows[0]) // 2
            for r, line in enumerate(rows):
                for k, ch in enumerate(line):
                    if ch != " ":
                        put(left + k, y - 2 + r, ch, BOLD + WHITE)
        else:
            x = round(cx + 0.82 * rx * math.cos(a))
            y = round(cy + 0.82 * ry * math.sin(a))
            s = str(hr)
            for k, ch in enumerate(s):
                put(x - len(s) // 2 + k, y, ch, BOLD + WHITE)
    return grid


def render(cols, rows, now):
    big_time = rows >= 34
    text_rows = 7 if big_time else 3

    ry = (rows - text_rows - 3) // 2
    rx = min(ry * 2, (cols - 4) // 2)
    ry = min(ry, rx // 2)
    if rx < 6 or ry < 3:
        return "Terminal too small - please enlarge it."

    big_numbers = ry >= 11 and rx >= 22
    grid = build_face(rx, ry, now, big_numbers)

    pad = " " * ((cols - (2 * rx + 1)) // 2)
    lines = [pad + "".join(f"{c}{ch}{RESET}" if c else ch for ch, c in row)
             for row in grid]

    lines.append("")
    if big_time:
        for row in big_text(now.strftime("%H:%M:%S")):
            lines.append(BOLD + CYAN + row.center(cols) + RESET)
    else:
        lines.append(BOLD + CYAN + now.strftime("%I:%M:%S %p").center(cols) + RESET)
    lines.append(DIM + now.strftime("%A, %d %B %Y").center(cols) + RESET)

    top = max(0, (rows - len(lines)) // 2)
    return "\n" * top + "\n".join(lines)


def main():
    sys.stdout.write("\033[?25l\033[2J")
    last_size, last_sec = None, None
    try:
        while True:
            size = shutil.get_terminal_size((80, 24))
            now = datetime.now()
            if size != last_size or now.second != last_sec:
                if size != last_size:
                    sys.stdout.write("\033[2J")
                frame = render(size.columns, size.lines, now)
                sys.stdout.write("\033[H" + frame.replace("\n", "\033[K\n") + "\033[J")
                sys.stdout.flush()
                last_size, last_sec = size, now.second
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")


if __name__ == "__main__":
    main()
