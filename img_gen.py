from PIL import Image, ImageDraw

import numpy as np

import time
from random import randint, gauss

from sympy import abc, sin, pi, nsolve
from math import cos, sqrt, ceil

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
    R_IM = 0.625  # Max dimension of image inside circular background, relative to background dimension
    R_SD = 0.25  # Mean ratio of shade added to bg theme color
    R_SD_SD = 0.0625  # Standard deviation on ratio of shade
    SD_A = 0.75  # Alpha channel for background inner wave
    ROT = 5  # General rotation angle range for bg
    R_GAP = 0.1  # Gap between image circles, as a ratio of the larger one

    def __init__(self, img_d, sz=4000, sz_img=200, theme=None, verbose=False):
        """
        :param img_d: Dictionary of image paths with ratio
        :param sz: Quality of single images generated, in pixel, particularly size of waveform SVG
        :param sz_img: Pixel size of final image cloud output
        :param theme: Theme color for circular background
        """
        self.img_d = img_d
        self.sz = sz
        self.sz_img = sz_img
        self.r = sz * self.R_BG
        self.iu = ImgUtil()
        self.verbose = verbose

        self.theme = theme

        self.img = None
        self.gen()

    def _draw_img_bg(self, ratio):
        """
        :param ratio: Ratio of circular bg container filled

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

        final = Image.alpha_composite(inner, outer)
        if self.verbose:
            final.save('bg.png')
            ic(f'Circular background generated with wave {idx}, quality {(sz, sz)}, shade {shade}, rotation {[ri, ro]}')
        return final

    def _draw_img(self, nm, ratio):
        img = self.iu.svg2img(f'icons/{nm}.svg', sz=self.r * self.R_IM * 2)

        bg = self._draw_img_bg(ratio)
        expand = Image.new('RGBA', bg.size, (0, 0, 0, 0))
        w_e, h_e = bg.size
        w, h = img.size
        expand.paste(img, [int((w_e - w) / 2), int((h_e - h) / 2)])

        final = Image.alpha_composite(bg, expand)
        if self.verbose:
            final.save('img.png')
            ic('Image with ratio background generated')
        return final

    def gen(self):
        imgs = self.img_d['imgs'].values()

        sz = ceil(sqrt(len(imgs))) * self.sz_img * 3  # Make sure canvas large enough
        ic(sz)
        self.img = Image.new('RGBA', (sz, sz), (255, 255, 255, 255))

        centers = dict()  # Image center coordinates, by type

        def _get_center(t, s):
            """
            :param t: Type of image
            :param s: Radius pixel size of image
            """
            def collide(x_i, y_i):
                margin = sz * self.R_MG
                if x_i < margin or x_i > sz - margin or y_i < margin or y_i > sz - margin:
                    return True

                for img in self.img_d['imgs'].values():
                    if 'center' in img:
                        xc_i, yc_i = img['center']
                        r_i = img['radius']
                        gap = self.R_GAP * max(s, r_i)

                        if sqrt((x_i - xc_i) ** 2 + (y_i - yc_i) ** 2) - s - r_i <= gap:
                            return True
                return False

            if t in centers:
                coords = np.array(centers[t])
                # ic(coords)
            else:  # First of type
                imgs_computed = list(filter(lambda i: 'center' in i, self.img_d['imgs'].values()))
                coords = list(map(lambda i: i['center'], imgs_computed))
                if len(coords) == 0:
                    coords = [
                        [sz/2, sz/2]
                    ]
                else:
                    coords = np.array(coords)
                # ic(coords)

            xc, yc = np.average(coords, axis=0)
            std_x, std_y = np.std(coords, axis=0)

            # ic(xc, yc, std_x, std_y)

            def get():
                return int(gauss(xc, max(std_x, s))), int(gauss(yc, max(std_y, s)))

            c = get()
            while collide(*c):
                c = get()

            if t in centers:
                centers[t].append(c)
            else:
                centers[t] = [c]
            return c

        for k, img in self.img_d['imgs'].items():
            tp = img['type'] if 'type' in img else 'Other'
            f = img['fluency']
            # ic(nm, tp, f)

            # sz_img = int(self.sz_img * sqrt(sqrt(f)))  # So that lower ratio are not too small
            sz_img = int(self.sz_img * (f ** (1. / 3)))  # So that lower ratio are not too small

            x, y = _get_center(tp, sz_img)
            self.img_d['imgs'][k]['center'] = (x, y)
            self.img_d['imgs'][k]['radius'] = sz_img

        ic(centers)

        for img in self.img_d['imgs'].values():
            nm = img['name']
            x, y = img['center']
            r = img['radius']
            ic(nm, r)
            img = self._draw_img(nm, 0.4)
            img = img.resize([r*2, r*2], Image.ANTIALIAS)
            expand = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
            expand.paste(img, [int(x - r/2), int(y - r/2)])
            self.img = Image.alpha_composite(self.img, expand)

        self.img.save(f'output/word-cloud {time.time()}.png')


if __name__ == '__main__':
    import json

    with open('example.json') as f:
        d = json.load(f)

        THEME = (255, 161, 70)
        ig = ImgGen(d, theme=THEME)

    # ic(get_segment_height(0.1))
