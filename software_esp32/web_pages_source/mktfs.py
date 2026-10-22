#!/usr/bin/env python3
"""
Generates ../src/tfs_data.c from the web pages in ./h

Cross platform replacement for zz.sh + mktfs.exe: every file in ./h is
gzipped and embedded as a C array, tfs_data[] lists them by name.

usage: python3 mktfs.py   (run from software_esp32/web_pages_source)

The css of index.html is generated with Tailwind, after changing classes run
tailwind/build.py first (needs Node.js).
"""

import gzip
import os
import re
import sys

SOURCE_DIR = "h"
OUTPUT_FILE = os.path.join("..", "src", "tfs_data.c")
FILES = [
    "blank.png",
    "favicon.ico",
    "index.html",
    "stmupdate.html",
    "warning_red.png",
    "warning_yellow.png",
    "window_close.png",
    "window_gray.png",
    "window_open.png",
]


def array_name(file_name):
    return "tfs____web_pages_" + re.sub(r"[^A-Za-z0-9]", "_", file_name)


def gzip_file(path):
    with open(path, "rb") as f:
        data = f.read()
    # fixed mtime, so the output only changes when the content changes
    return gzip.compress(data, compresslevel=9, mtime=0)


def c_array(file_name, data):
    lines = ["static const unsigned char %s[] = {" % array_name(file_name),
             "\t/* ../web_pages/%s */" % file_name]
    for i in range(0, len(data), 10):
        chunk = ", ".join("0x%02x" % b for b in data[i:i + 10])
        lines.append("\t" + chunk + ("," if i + 10 < len(data) else ""))
    lines.append("};")
    return "\n".join(lines)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    parts = ["#include <tfs.h>", "", "extern const TFS_DIR_ENTRY tfs_data[];", ""]
    for file_name in FILES:
        parts.append(c_array(file_name, gzip_file(os.path.join(SOURCE_DIR, file_name))))
        parts.append("")
    parts.append("const TFS_DIR_ENTRY tfs_data[] = {")
    for file_name in FILES:
        name = array_name(file_name)
        parts.append('\t{ "/%s", 0, (unsigned char*)%s, sizeof(%s) },' % (file_name, name, name))
    parts.append("\t{ 0, 0, 0, 0 }")
    parts.append("};")
    parts.append("")
    with open(OUTPUT_FILE, "w", newline="\n") as f:
        f.write("\n".join(parts))
    print("written " + OUTPUT_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
