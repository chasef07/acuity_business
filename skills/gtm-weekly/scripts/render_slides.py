#!/usr/bin/env python3
"""Render one PNG per slide of a .pptx with macOS Quick Look, for visual QA.

Quick Look only renders a deck's first slide, so this writes one copy of the
deck per slide with that slide moved to the front, then thumbnails each copy.

Usage: render_slides.py deck.pptx out_dir
"""

import re
import subprocess
import sys
import zipfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    deck, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(deck) as z:
        parts = {info.filename: (info, z.read(info.filename)) for info in z.infolist()}
    presentation = parts["ppt/presentation.xml"][1].decode()
    id_list = re.search(r"<p:sldIdLst>.*?</p:sldIdLst>", presentation, re.S).group(0)
    ids = re.findall(r"<p:sldId [^>]*/>", id_list)

    copies = []
    for n in range(1, len(ids) + 1):
        order = [ids[n - 1]] + ids[: n - 1] + ids[n:]
        xml = presentation.replace(id_list, "<p:sldIdLst>" + "".join(order) + "</p:sldIdLst>")
        copy = out / f"slide-{n:02d}.pptx"
        with zipfile.ZipFile(copy, "w", zipfile.ZIP_DEFLATED) as z:
            for name, (info, data) in parts.items():
                z.writestr(info, xml if name == "ppt/presentation.xml" else data)
        copies.append(copy)

    procs = [subprocess.Popen(["qlmanage", "-t", "-s", "1400", "-o", str(out), str(c)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for c in copies]
    for p in procs:
        p.wait()

    missing = []
    for copy in copies:
        png = copy.with_name(copy.name + ".png")
        if png.exists():
            print(png)
        else:
            missing.append(copy.name)
        copy.unlink()
    if missing:
        print("not rendered: " + ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
