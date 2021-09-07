import numpy as np

from PIL import Image, ImageDraw
from pathlib import Path

from icecream import ic


class ImgUtil:
    @staticmethod
    def circle_bbox(x, y, r):
        return list(map(int, [x-r, y-r, x+r, y+r]))

    @staticmethod
    def draw_circle(img, x, y, r, outline=None, fill=None, width=1):
        draw = ImageDraw.Draw(img)
        bbox = ImgUtil.circle_bbox(x, y, r)
        draw.ellipse(bbox, outline=outline, fill=fill, width=width)
        ic(f'Ellipse drawn with bounding box {bbox}')

    @staticmethod
    def svg2img(f, sz=4000):
        """
        Converts an SVG file to a pillow image
        """
        fnm = Path(f).stem
        from cairosvg import svg2png
        s = open(f, 'rb').read()
        svg2png(bytestring=s, parent_width=sz, parent_height=sz, write_to=f'{fnm}.png')
        ic(f'SVG converted to PNG file: {fnm}.png')
        return Image.open(f'{fnm}.png')

    @staticmethod
    def refill_color(
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
        ic(f'Image filled with {c_ori} converted to {c_new}')
        # img_new.show()
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

    @staticmethod
    def sweep_alpha(img, f):
        arr = np.array(img)
        r, g, b, a = arr.T
        arr[..., -1] = a.T * f
        img_new = Image.fromarray(arr)
        # img_new.show()
        ic(f'Image alpha channel multiplied by {f}')
        return img_new
