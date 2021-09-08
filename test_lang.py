from cairosvg import svg2png

from PIL import Image
import numpy as np

from icecream import ic

from img_util import ImgUtil

if __name__ == '__main__':
    # s = open("assets/wave 1.svg", "rb").read()
    # ic(s)
    #
    # svg2png(bytestring=s, parent_width=4000, parent_height=4000, write_to="output.png")
    # ImgUtil.svg2png('assets/wave 1.svg')

    # im = Image.open('wave 1.png')

    # data = np.array(im)   # "data" is a height x width x 4 numpy array
    # red, green, blue, alpha = data.T # Temporarily unpack the bands for readability
    #
    # # Replace white with red... (leaves alpha values alone...)
    # white_areas = (red == 0) & (blue == 0) & (green == 0)
    # data[..., :-1][white_areas.T] = (255, 0, 0) # Transpose back needed
    #
    # im2 = Image.fromarray(data)
    # im2.show()

    # THEME = (255, 161, 70)
    # c = Iu.lightness(THEME, 0.25)
    # ic(c)
    #
    # im = Iu.refill_color(im, (0, 0, 0), c)
    # # im.putalpha(127)
    # # im.show()
    #
    # im = Iu.sweep_alpha(im, 0.75)

    iu = ImgUtil()
    #
    # # iu.svg2img('icons/Figma.svg', sz=600 * 0.75 * 2)
    # # ic(Image.open('icons/Figma, 900.png').size)
    #
    # # Iu.svg2img('assets/wave 1.svg', sz=600 * 0.75 * 2)
    #
    # a = '1'
    # d = {}
    # d[a] = 2
    # ic(d[a])
    #
    # ic(np.std([1, 200]))
    # ic(np.std([1]))

    iu.svg2img('icons/PyTorch, modified.svg', sz=600)

    ic('#%02x%02x%02x' % (0, 128, 64))
