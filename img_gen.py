from PIL import Image, ImageDraw

from icecream import ic
import time
from random import randint, gauss

from img_util import ImgUtil as Iu


def get_segment_height(a):
    """
    :param a: Ratio of a circle's area
    :return: Segment height in range [-1, 1] (offset by circle's center)

    Assumes radius of 1
    """
    from sympy import Symbol, solve, sin, cos, pi, Eq, nsolve, abc
    from math import cos

    # measurements = [(5.71403, 0.347064), (4.28889, -0.396854), (5.78091, -7.29133e-05),
    #                 (2.06098, 0.380579), (8.13321, 0.272391), (8.23589, -0.304111), (6.53473, 0.265354), (1.6023,
    #                                                                                                       0.131908)]
    #
    # x = Symbol('x')
    # eq = (2p )
    #
    # eq1 = Eq(a * sin((2.0 * pi * f * measurements[0][0]) + phi) - measurements[0][1])
    # eq2 = Eq(a * sin((2.0 * pi * f * measurements[4][0]) + phi) - measurements[4][1])
    # eq3 = Eq(a * sin((2.0 * pi * f * measurements[6][0]) + phi) - measurements[6][1])
    # solve((eq1, eq2, eq3), (a, f, phi))
    x = abc.x
    # ic(nsolve(sin(x), x, 2))
    # ic(2 * pi * a)
    theta = nsolve(x - sin(x) - 2 * pi * a, 1)
    return 1 - cos(theta / 2) - 1


class ImgGen:
    N_VW = 9  # Number of wave SVGs

    def __init__(self, img_d, sz=5000, theme=None):
        self.sz = sz
        self.theme = theme

        self.img = Image.new("RGBA", (sz, sz), (255, 255, 255, 0))
        self._draw()
        # self.img.show()
        # self.img.save(f'output/word-cloud {time.time()}.png')

    def _draw_img_bg(self, ratio, sz=4000):
        """
        :param ratio: Ratio of circular bg container filled
        :param sz: Quality of the background, used as pixel size of waveform SVG

        Generates image backgrounds, which are circles filled with random waveforms
        """
        i = randint(1, self.N_VW)
        wave = Iu.svg2img(f'assets/wave {i}.svg', sz=sz)
        dummy_bg = Image.new('RGBA', wave.size, 255)

        r = sz * 0.15
        margin = int(sz * 0.2)

        bbox_p = (randint(margin, sz - margin), int(sz * 0.5 + r * get_segment_height(ratio)), r)
        bbox = Iu.circle_bbox(*bbox_p)

        mask = Image.new('RGBA', wave.size, (0, 0, 0, 255))
        Iu.draw_circle(mask, *bbox_p, fill=255)

        inner = Image.composite(dummy_bg, wave, mask)
        inner = inner.crop(bbox)
        shade = 0.25 + gauss(0, 0.0625)
        inner = Iu.refill_color(inner, (0, 0, 0), Iu.lightness(self.theme, shade))
        inner = Iu.sweep_alpha(inner, 0.75)
        ri, ro = gauss(0, 5), gauss(0, 5)
        inner = inner.rotate(ri)

        outer = Iu.svg2img('assets/img-circle.svg', sz=r * 2)
        outer = outer.rotate(ro)

        ic(f'Circular background generated with wave {i}, quality {(sz, sz)}, shade {shade}, rotation {[ri, ro]}')
        final = Image.alpha_composite(inner, outer)

        # outer.paste(inner)
        final.save('final.png')

    def _draw(self):
        # bg = Iu.svg2img('assets/img-circle.svg', sz=4000)
        self._draw_img_bg(0.8)

        # self._draw_img_bg()


if __name__ == '__main__':
    THEME = (255, 161, 70)
    ig = ImgGen({}, theme=THEME)

    # ic(get_segment_height(0.1))
