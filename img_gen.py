from PIL import Image, ImageDraw

import time
from pathlib import Path


class ImgUtil:
    @staticmethod
    def svg2png(f, sz=4000):
        fnm = Path(f).stem
        from cairosvg import svg2png
        s = open(f, 'rb').read()
        svg2png(bytestring=s, parent_width=sz, parent_height=sz, write_to=f'{fnm}.png')
        print(f'PNG file written: {fnm}.png')


class ImgGen:
    def __init__(self, img_d, sz=5000, theme=None):
        self.sz = sz
        self.theme = theme
        self.img = Image.new("RGBA", (sz, sz), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.img)
        self._draw()
        self.img.show()
        self.img.save(f'output/word-cloud {time.time()}.png')

    def _draw_circle(self, x, y, r, outline=None):
        self.draw.ellipse([x-r, y-r, x+r, y+r], outline=outline, fill=None, width=self.sz // 500)

    def _draw_img_bg(self, img):
        print(img.size)

    def _draw(self):
        self._draw_circle(400, 400, 200, outline=self.theme)


if __name__ == '__main__':
    THEME = (255, 161, 70)
    ig = ImgGen({}, theme=THEME)