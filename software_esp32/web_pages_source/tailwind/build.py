#!/usr/bin/env python3
"""
Builds the Tailwind CSS of ../h/index.html and writes it into the <style> block of the page,
between the markers /* tailwind:start */ and /* tailwind:end */.

Needs Node.js, Tailwind is fetched by npx (pinned version).
Afterwards run ../mktfs.py to update src/tfs_data.c.

usage: python3 build.py   (run from software_esp32/web_pages_source/tailwind)
"""

import os
import re
import subprocess
import sys
import tempfile

TAILWIND = "tailwindcss@3.4.17"
HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "..", "h", "index.html")
START, END = "/* tailwind:start */", "/* tailwind:end */"
BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)


def main():
    with open(PAGE, encoding="utf-8") as f:
        page = f.read()
    if not BLOCK.search(page):
        sys.exit("markers %s ... %s not found in %s" % (START, END, PAGE))

    with tempfile.TemporaryDirectory() as tmp:
        # scan the page without the generated css, so removed classes do not stay
        content = os.path.join(tmp, "index.html")
        with open(content, "w", encoding="utf-8") as f:
            f.write(BLOCK.sub(START + END, page))
        css_file = os.path.join(tmp, "out.css")
        subprocess.run(["npx", "--yes", TAILWIND, "-c", os.path.join(HERE, "tailwind.config.js"),
                        "-i", os.path.join(HERE, "input.css"), "--content", content,
                        "-o", css_file, "--minify"], check=True)
        with open(css_file, encoding="utf-8") as f:
            css = f.read().strip()

    page = BLOCK.sub(lambda m: START + "\n" + css + "\n" + END, page)
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(page)
    print("%s: %d bytes css" % (os.path.relpath(PAGE), len(css)))


if __name__ == "__main__":
    main()
