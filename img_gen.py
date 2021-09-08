from PIL import Image, ImageDraw

import numpy as np

import time
from random import randint, gauss
from pathlib import Path

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


def color_tup2hex(c):
    return '%02x%02x%02x' % tuple(c)


def write_bg_circle(color):
    c_h = color_tup2hex(color)
    content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\
                    <defs>\
                        <style>.cls-1{{fill:#{c_h};}}.cls-2{{fill:#{c_h};}}</style>\
                    </defs>\
                    <g id="Layer_2" data-name="Layer 2">\
                        <g id="Layer_1-2" data-name="Layer 1">\
                            <path class="cls-1"\
                                  d="M50,99.55A49.52,49.52,0,0,1,12.38,17.79a48,48,0,1,0,75.24,0A49.52,49.52,0,0,1,50,99.55Z"/>\
                            <path class="cls-2"\
                                  d="M96.9,35.47a49.09,49.09,0,1,1-93.8,0,48.41,48.41,0,1,0,95.31,12,48.71,48.71,0,0,0-1.51-12M50,0A47.5,47.5,0,1,1,2.5,47.5,47.5,47.5,0,0,1,50,0a50,50,0,1,0,50,50A50,50,0,0,0,50,0Z"/>\
                        </g>\
                    </g>\
                </svg>'

    file = open(f'assets/bg-circle, {c_h}.svg', 'w')
    file.write(content)
    file.close()


class ImgGen:
    N_VW = 9  # Number of wave SVGs
    R_BG = 0.15  # Ratio to generate circular background, relative to global `sz`
    R_MG = 0.2  # Ratio of margin for background generation
    R_IM = 0.625  # Max dimension of image inside circular background, relative to background dimension
    R_SD = 0.25  # Mean ratio of shade added to bg theme color
    R_SD_SD = 0.0625  # Standard deviation on ratio of shade
    SD_A = 0.75  # Alpha channel for background inner wave
    ROT = 5  # General rotation angle range for bg
    R_GAP = 0.15  # Gap between image circles, as a ratio of the larger one
    R_OVL = 0.125  # Ratio for overlay

    def __init__(self, img_d, sz=4000, sz_img=200, verbose=False, overlay=False):
        """
        :param img_d: Dictionary of image paths with ratio
        :param sz: Quality of single images generated, in pixel, particularly size of waveform SVG
        :param sz_img: Pixel size of final image cloud output
        :param overlay: If true, images are overlaid based on type color
        """
        self.img_d = img_d

        for k, img in self.img_d['imgs'].items():
            if 'type' not in img:
                img['type'] = 'Other'

        self.sz = sz
        self.sz_img = sz_img
        self.r = sz * self.R_BG
        self.iu = ImgUtil()
        self.verbose = verbose
        self.overlay = overlay

        self.theme = img_d['theme']
        self.is_d_theme = type(self.theme) is dict

        self.img = None
        self.gen()

    def _draw_img_bg(self, ratio, typ):
        """
        :param ratio: Ratio of circular bg container filled
        :param typ: Type of image

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
        color = self.theme[typ] if self.is_d_theme else self.theme
        inner = self.iu.refill_color(inner, (0, 0, 0), self.iu.lightness(color, shade))
        inner = self.iu.sweep_alpha(inner, self.SD_A)
        ri, ro = gauss(0, self.ROT), gauss(0, self.ROT)
        inner = inner.rotate(ri)

        fnm = f'assets/bg-circle, {color_tup2hex(color)}.svg'
        if not Path(fnm).exists():
            write_bg_circle(color)

        outer = self.iu.svg2img(fnm, sz=r * 2)
        outer = self.iu.refill_color(outer, (255, 161, 70), color)
        outer = outer.rotate(ro)

        final = Image.alpha_composite(inner, outer)
        if self.verbose:
            final.save('bg.png')
            ic(f'Circular background generated with wave {idx}, quality {(sz, sz)}, shade {shade}, rotation {[ri, ro]}')
        return final

    def _draw_img(self, k, ratio):
        img_obj = self.img_d['imgs'][k]
        nm = img_obj['name']
        typ = img_obj['type']
        img = self.iu.svg2img(f'icons/{nm}.svg', sz=int(self.r * self.R_IM * 2))
        if self.overlay:
            color_overlay = list(self.theme[typ])
            color_overlay.append(int(255 * self.R_OVL))
            dummy_bg = Image.new('RGBA', img.size, tuple(color_overlay))
            overlay = Image.composite(dummy_bg, img, img)
            img = Image.alpha_composite(img, overlay)

        bg = self._draw_img_bg(ratio, img_obj['type'])
        expand = Image.new('RGBA', bg.size, (0, 0, 0, 0))  # Same format for `alpha_composite`
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
            f = img['fluency']
            # ic(nm, tp, f)

            sz_img = int(self.sz_img * sqrt(f))  # So that lower ratio are not too small
            # sz_img = int(self.sz_img * (f ** (1. / 3)))  # So that lower ratio are not too small

            x, y = _get_center(img['type'], sz_img)
            self.img_d['imgs'][k]['center'] = (x, y)
            self.img_d['imgs'][k]['radius'] = sz_img

        ic(centers)

        for k, img in self.img_d['imgs'].items():
            x, y = img['center']
            r = img['radius']
            ratio = img['fluency']
            ic(k, r)
            img = self._draw_img(k, ratio)
            img = img.resize([r*2, r*2], Image.ANTIALIAS)
            expand = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
            expand.paste(img, [int(x - r/2), int(y - r/2)])
            self.img = Image.alpha_composite(self.img, expand)

        self.img.save(f'output/image-cloud {time.time()}.png')


if __name__ == '__main__':
    import json

    with open('example.json') as f:
        d = json.load(f)

        THEME = (255, 161, 70)
        ig = ImgGen(d, overlay=True)
