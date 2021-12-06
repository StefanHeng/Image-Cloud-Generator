import os
from random import randint, gauss
from pathlib import Path
from math import cos, sqrt, ceil
import pickle

from PIL import Image
import numpy as np
from sympy import abc, sin, pi, nsolve
from icecream import ic

from util import *
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
    SD_A = 0.75  # Alpha for background inner wave
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

    def _draw_img_bg(self, ratio, typ):
        """
        Generates image backgrounds, which are circles filled with random waveforms

        :param ratio: Ratio of circular bg container filled
        :param typ: Type of image
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
        expand.paste(img, (int((w_e - w) / 2), int((h_e - h) / 2)))

        final = Image.alpha_composite(bg, expand)
        if self.verbose:
            final.save('img.png')
            ic('Image with ratio background generated')
        return final

    def __call__(self, r=1.0, patience=1e4, count=None, save=False):
        """
        Create image cloud

        :param r: Relative ratio of image to the canvas
        :param patience: Restart image center generations after `patience` iterations
        """
        imgs = self.img_d['imgs'].values()

        sz = int(ceil(sqrt(len(imgs))) * self.sz_img * 3 * r)  # Make sure canvas large enough
        # ic(sz)
        self.img = Image.new('RGBA', (sz, sz), (255, 255, 255, 255))

        class Patience:
            def __init__(self):
                self.count = 0
                self.p = patience

            def inc(self):
                self.count += 1

            def reached(self):
                return self.count > self.p

        def _get_centers():
            p = Patience()

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

                    for img__ in self.img_d['imgs'].values():
                        if 'center' in img__:
                            xc_i, yc_i = img__['center']
                            r_i = img__['radius']
                            gap = self.R_GAP * max(s, r_i)

                            if sqrt((x_i - xc_i) ** 2 + (y_i - yc_i) ** 2) - s - r_i <= gap:
                                return True
                    return False

                if t in centers:
                    coords = np.array(centers[t])
                else:  # First of type
                    imgs_computed = list(filter(lambda im: 'center' in im, self.img_d['imgs'].values()))
                    coords = list(map(lambda im: im['center'], imgs_computed))
                    if len(coords) == 0:
                        coords = [
                            [sz/2, sz/2]
                        ]
                    else:
                        coords = np.array(coords)

                xc, yc = np.average(coords, axis=0)
                std_x, std_y = np.std(coords, axis=0)

                def get():
                    p.inc()
                    return int(gauss(xc, max(std_x, s))), int(gauss(yc, max(std_y, s)))

                coord = get()
                if p.reached():
                    return False
                while collide(*coord):
                    if p.reached():
                        return False
                    coord = get()

                if t in centers:
                    centers[t].append(coord)
                else:
                    centers[t] = [coord]
                return coord

            for _, img_ in self.img_d['imgs'].items():
                flu = img_['fluency']

                sz_img = int(self.sz_img * sqrt(flu))  # So that lower ratio are not too small
                # sz_img = int(self.sz_img * (f ** (1. / 3)))

                center = _get_center(img_['type'], sz_img)
                if center:
                    # x, y = center
                    # ic(type(center), center)
                    img_['center'] = center
                    img_['radius'] = sz_img
                else:
                    return False

            return centers

        cts = _get_centers()
        while not cts:
            for _, img in self.img_d['imgs'].items():
                img.pop('center', None)
                img.pop('radius', None)
            cts = _get_centers()
        print(f'{now()}| Image coordinates generated... ')

        for k, img in self.img_d['imgs'].items():
            x, y = img['center']
            r = img['radius']
            ratio = img['fluency']
            # ic(k, r)
            img = self._draw_img(k, ratio)
            img = img.resize((r*2, r*2), Image.ANTIALIAS)
            expand = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
            expand.paste(img, (int(x - r/2), int(y - r/2)))
            self.img = Image.alpha_composite(self.img, expand)

        fnm = os.path.join('output', f'image-cloud, {now()}, {count}.png')
        if save:
            ic(os.path.splitext(fnm))
            with open(ch_ext(fnm, 'pickle'), 'wb') as handle:
                pickle.dump(cts, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print(f'{now()}| Generated coordinates written to pickle ')
        self.img.save(f'output/image-cloud, {now()}, {count}.png')
        print(f'{now()}| Image ({sz} x {sz}) generated and written to {fnm}')

    @staticmethod
    def make_n(dic, n=5, obj_kwargs=None, call_kwargs=None):
        """
        Make multiple image clouds with the same image dictionary

        :param dic: Image dictionary
        :param n: Number of repetitions
        :param obj_kwargs: Arguments passed to object constructor
        :param call_kwargs: Arguments passed to object call
        """
        for i in range(n):
            print(f'{now()}| Creating image cloud #{i+1}')
            ig = ImgGen(dic, **obj_kwargs)
            ig(count=i+1, **call_kwargs)


if __name__ == '__main__':
    import json

    with open('example.json') as f:
        d = json.load(f)

        # THEME = (255, 161, 70)
        ImgGen.make_n(d, obj_kwargs=dict(overlay=True), call_kwargs=dict(r=0.75, save=True))

    def reuse_pickle():
        fnm = 'gird-search, [(-5, 5), (-5, 5), 0.25], [(0, 1), 0.05], 2021-12-06 00:00:37.pickle'
        with open(fnm, 'rb') as handle:
            d = pickle.load(handle)
