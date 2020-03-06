#!/usr/bin/env python3

import cairo
import json
import mapnik
import os
import os.path
import subprocess
import sys

mml = "/home/sjoerd/openstreetmap-carto/project.mml"
carto = "/home/sjoerd/kosmtik/node_modules/.bin/carto"
dest = "/home/sjoerd/export/map.pdf"


def run_carto(mml_path):
    res = subprocess.run(
        ["/usr/bin/git", "rev-parse", "--short", "HEAD"], capture_output=True
    )
    filename = "mapnik-%s.xml" % res.stdout.decode("ASCII").strip()
    if not os.path.exists(filename):
        subprocess.run([carto, "-f", filename, mml_path])
    return filename


def main(specfile):
    spec = readspec(specfile)
    render_map(spec)


def render_map(spec):
    os.chdir(os.path.dirname(mml))
    mapfile = run_carto(mml)

    mapnik_map = mapnik.Map(*spec.mapsize)
    mapnik.load_map(mapnik_map, mapfile)
    mapnik_map.zoom_to_box(spec.bbox)

    if spec.layers:
        for l in mapnik_map.layers:
            l.active = l.name in spec.layers

    scale = 2
    scale_factor = 1 / scale

    print("Map size:            ", spec.mapsize)
    print("Scale factor:        ", scale_factor)
    print("Actual envelope:     ", mapnik_map.envelope())
    print("Scale:               ", mapnik_map.scale() * scale)
    print("Scale denominator:   ", mapnik_map.scale_denominator() * scale_factor)
    print(
        "Zoom level:          ",
        get_zoom_level(mapnik_map.scale_denominator() * scale_factor),
    )

    if dest.endswith("pdf"):
        surface = cairo.PDFSurface(dest, mapnik_map.width, mapnik_map.height)
    elif dest.endswith("svg"):
        surface = cairo.SVGSurface(dest, mapnik_map.width, mapnik_map.height)
    else:
        surface = mapnik.Image(mapnik_map.width, mapnik_map.height)

    mapnik.render(mapnik_map, surface, scale_factor, 0, 0)

    try:
        surface.finish()
    except:
        surface.save(dest, "png")


def readspec(specfile):
    with open(specfile) as fp:
        data = json.load(fp)
    return MapSpec(data)


class MapSpec:
    def __init__(self, data):
        # bbox: coordinates on the ground
        # mapsize: desired size in pts or pixels
        # oversize: size in pixels we render the map at
        self.bbox = mapnik.Box2d(*data["bbox"])
        self.mapsize = paper[data["size"]]
        self.layers = data.get("layers")
        if data["orientation"] == "landscape":
            self.mapsize = (self.mapsize[1], self.mapsize[0])
        # self.oversize = [int(k * 2) for k in self.mapsize]


paper = {
    "A0": (2384, 3371),
    "A1": (1685, 2384),
    "A2": (1190, 1684),
    "A3": (842, 1190),
    "A4": (595, 842),
}


zoomlevels = {
    0: 1000000000,
    1: 500000000,
    2: 200000000,
    3: 100000000,
    4: 50000000,
    5: 25000000,
    6: 12500000,
    7: 6500000,
    8: 3000000,
    9: 1500000,
    10: 750000,
    11: 400000,
    12: 200000,
    13: 100000,
    14: 50000,
    15: 25000,
    16: 12500,
    17: 5000,
    18: 2500,
    19: 1500,
    20: 750,
    21: 500,
    22: 250,
    23: 100,
    24: 50,
    25: 25,
    26: 12.5,
}


def get_zoom_level(scale_denominator):
    for zl, sd in zoomlevels.items():
        if sd < scale_denominator:
            return zl - 1
    return None


if __name__ == "__main__":
    main(sys.argv[1])
