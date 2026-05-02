#!/usr/bin/env python3
from __future__ import annotations

import re
import sys


def main() -> None:
    with open(sys.argv[1]) as f:
        first_line = f.readline().strip()

    pattern = r"^NEM-\d+: [a-z].{9,}$"
    if re.match(pattern, first_line):
        sys.exit(0)

    print(f"Bad commit message: {first_line!r}")
    print("  Format : NEM-XX: description")
    print("  Rules  : ticket uppercase, lowercase description, at least 10 chars")
    print("  Example: NEM-6: add user aggregate root")
    sys.exit(1)


if __name__ == "__main__":
    main()
