#!/usr/bin/env python3

import mapnik
import cairo
import subprocess
import os
import os.path

mml = "/home/sjoerd/openstreetmap-carto/project.mml"
carto = "/home/sjoerd/kosmtik/node_modules/.bin/carto"
dest = "/home/sjoerd/export/export.pdf"

os.chdir(os.path.dirname(mml))


def run_carto(mml_path):
    res = subprocess.run(
        ["/usr/bin/git", "rev-parse", "--short", "HEAD"], capture_output=True
    )
    filename = "mapnik-%s.xml" % res.stdout.decode("ASCII").strip()
    if not os.path.exists(filename):
        subprocess.run([carto, "-f", filename, mml_path])
    return filename


mapfile = run_carto(mml)

A4 = (595, 842)

mapnik_map = mapnik.Map(*A4)
mapnik.load_map(mapnik_map, mapfile)
bbox = mapnik.Box2d(645653, 6872776, 656785, 6891041)
mapnik_map.zoom_to_box(bbox)

# Or write to PDF
scale_factor = 1684 / 5000
surface = cairo.PDFSurface(dest, mapnik_map.width, mapnik_map.height)
mapnik.render(mapnik_map, surface, scale_factor, 0, 0)
surface.finish()
