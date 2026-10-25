"""Generate PWA home-screen icons for Patente B."""
from PIL import Image, ImageDraw
import math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "public_html", "icons")
os.makedirs(OUT, exist_ok=True)


def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = int(size * 0.18)

    # Rounded square — Italian green
    def rrect(x0, y0, x1, y1, fill):
        d.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
        d.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
        for ex, ey in [(x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)]:
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=fill)

    rrect(0, 0, size, size, (0, 146, 70, 255))  # #009246

    # Steering wheel
    outer_r  = size * 0.36
    hub_r    = size * 0.10
    spoke_w  = max(2, int(size * 0.055))
    ring_w   = max(2, int(size * 0.068))

    d.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
              outline=(255, 255, 255, 255), width=ring_w)

    for deg in (90, 210, 330):
        a = math.radians(deg)
        xi = cx + math.cos(a) * (hub_r + spoke_w * 0.5)
        yi = cy - math.sin(a) * (hub_r + spoke_w * 0.5)
        xo = cx + math.cos(a) * (outer_r - ring_w)
        yo = cy - math.sin(a) * (outer_r - ring_w)
        d.line([(xi, yi), (xo, yo)], fill=(255, 255, 255, 255), width=spoke_w)

    d.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r],
              fill=(255, 255, 255, 255))

    return img


for size in (192, 512):
    path = os.path.join(OUT, f"icon-{size}.png")
    make_icon(size).save(path, "PNG")
    print(f"saved {path}")
