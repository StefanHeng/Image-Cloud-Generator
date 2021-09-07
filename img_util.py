import numpy as np

from PIL import Image, ImageDraw
from pathlib import Path
from cairosvg import svg2png
from icecream import ic


class ImgUtil:
    def __init__(self, verbose=False):
        self.verbose = verbose

    @staticmethod
    def circle_bbox(x, y, r):
        return list(map(int, [x-r, y-r, x+r, y+r]))

    def draw_circle(self, img, x, y, r, outline=None, fill=None, width=1):
        draw = ImageDraw.Draw(img)
        bbox = ImgUtil.circle_bbox(x, y, r)
        draw.ellipse(bbox, outline=outline, fill=fill, width=width)
        if self.verbose:
            ic(f'Ellipse drawn with bounding box {bbox}')

    def svg2img(self, f, sz=4000):
        """
        Converts an SVG file to a pillow image
        """
        fnm = Path(f).with_suffix('')  # Remove file ext.
        sz = int(sz)
        fnm_png = f'{fnm}, {sz}.png'

        if not Path(fnm_png).exists():
            s = open(f, 'rb').read()
            svg2png(bytestring=s, parent_width=sz, parent_height=sz, write_to=fnm_png)
            if self.verbose:
                ic(f'SVG converted to PNG file: {fnm_png}')
        else:
            if self.verbose:
                ic(f'Using converted PNG file: {fnm_png}')

        im = Image.open(fnm_png)
        w, h = im.size
        if w > sz or h > sz:
            im.thumbnail((sz, sz), Image.ANTIALIAS)
            im.save(fnm_png)
        return im

    def refill_color(
            self,
            img,
            c_ori: tuple[int, int, int],
            c_new: tuple[int, int, int]
    ):
        arr = np.array(img)
        r, g, b, a = arr.T
        r_o, g_o, b_o = c_ori
        area = (r == r_o) & (b == b_o) & (g == g_o)
        arr[..., :-1][area.T] = c_new

        img_new = Image.fromarray(arr)
        if self.verbose:
            ic(f'Image filled with {c_ori} converted to {c_new}')
        return img_new

    @staticmethod
    def lightness(c, f):
        """
        :return: Original color in a different shade/tint

        Positive `f` for tint, negative for shade
        """
        if f == 0:
            return c
        else:
            c_new = tuple(map(
                (lambda x: x + (255 - x) * f) if f > 0 else (lambda x: x * (1 + f)),
                c
            ))
            return tuple(map(int, c_new))

    def sweep_alpha(self, img, f):
        arr = np.array(img)
        r, g, b, a = arr.T
        arr[..., -1] = a.T * f
        img_new = Image.fromarray(arr)
        if self.verbose:
            ic(f'Image alpha channel multiplied by {f}')
        return img_new
