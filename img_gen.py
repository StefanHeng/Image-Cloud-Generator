from PIL import Image, ImageDraw

import time
from random import randint, gauss

from sympy import abc, sin, pi, nsolve
from math import cos

from icecream import ic

from img_util import ImgUtil


def get_segment_height(a):
    """
    :param a: Ratio of a circle's area
    :return: Segment height in range [-1, 1] (offset by circle's center)

    Assumes radius of 1
    """
    x = abc.x
    theta = nsolve(x - sin(x) - 2 * pi * a, 1)
    return 1 - cos(theta / 2) - 1


class ImgGen:
    N_VW = 9  # Number of wave SVGs
    R_BG = 0.15  # Ratio to generate circular background, relative to global `sz`
    R_MG = 0.2  # Ratio of margin for background generation
    R_IM = 0.75  # Max dimension of image inside circular background, relative to background dimension
    R_SD = 0.25  # Mean ratio of shade added to bg theme color
    R_SD_SD = 0.0625  # Standard deviation on ratio of shade
    SD_A = 0.75  # Alpha channel for background inner wave
    ROT = 5  # General rotation angle range for bg

    def __init__(self, img_d, sz=4000, theme=None):
        self.sz = sz
        self.r = sz * self.R_BG
        self.iu = ImgUtil()

        self.theme = theme

        self.img = Image.new("RGBA", (sz, sz), (255, 255, 255, 0))
        self._draw()
        # self.img.show()
        # self.img.save(f'output/word-cloud {time.time()}.png')

    def _draw_img_bg(self, ratio):
        """
        :param ratio: Ratio of circular bg container filled
        :param sz: Quality of the background, used as pixel size of waveform SVG

        Generates image backgrounds, which are circles filled with random waveforms
        """
        sz = self.sz
        r = self.r

        idx = randint(1, self.N_VW)
        wave = self.iu.svg2img(f'assets/wave {idx}.svg', sz=sz)
        dummy_bg = Image.new('RGBA', wave.size, 255)

        margin = int(sz * self.R_MG)

        bbox_p = (randint(margin, sz - margin), int(sz * 0.5 + r * get_segment_height(ratio)), r)
        bbox = self.iu.circle_bbox(*bbox_p)

        mask = Image.new('RGBA', wave.size, (0, 0, 0, 255))
        self.iu.draw_circle(mask, *bbox_p, fill=255)

        inner = Image.composite(dummy_bg, wave, mask)
        inner = inner.crop(bbox)
        shade = self.R_SD + gauss(0, self.R_SD_SD)
        inner = self.iu.refill_color(inner, (0, 0, 0), self.iu.lightness(self.theme, shade))
        inner = self.iu.sweep_alpha(inner, self.SD_A)
        ri, ro = gauss(0, self.ROT), gauss(0, self.ROT)
        inner = inner.rotate(ri)

        outer = self.iu.svg2img('assets/img-circle.svg', sz=r * 2)
        outer = outer.rotate(ro)

        ic(f'Circular background generated with wave {idx}, quality {(sz, sz)}, shade {shade}, rotation {[ri, ro]}')
        final = Image.alpha_composite(inner, outer)

        final.save('bg.png')
        return final

    def _draw_img(self, img, ratio):
        bg = self._draw_img_bg(ratio)
        expand = Image.new('RGBA', bg.size, (0, 0, 0, 0))
        expand.paste(img, ((int((bg.size[0] - img.size[0]) / 2)),) * 2)

        final = Image.alpha_composite(bg, expand)
        final.save('final.png')
        ic('Image with ratio background generated')
        return final

    def _draw(self):
        im = self.iu.svg2img('icons/CLion.svg', sz=self.r * self.R_IM * 2)
        self._draw_img(im, 0.4)


if __name__ == '__main__':
    THEME = (255, 161, 70)
    ig = ImgGen({}, theme=THEME)

    # ic(get_segment_height(0.1))
