from cairosvg import svg2png

from img_gen import ImgUtil

if __name__ == '__main__':
    # s = open("assets/wave 1.svg", "rb").read()
    # print(s)
    #
    # svg2png(bytestring=s, parent_width=4000, parent_height=4000, write_to="output.png")
    ImgUtil.svg2png('assets/wave 1.svg')
