import os
import re
import sys
import logging
import datetime
import colorama
from typing import Dict, Tuple, Union
from collections import OrderedDict

import sty
from icecream import ic


def now(as_str=True, sep=':'):
    d = datetime.datetime.now()
    return d.strftime(f'%Y-%m-%d %H{sep}%M{sep}%S') if as_str else d  # Considering file output path


def ch_ext(fnm, ext):
    """
    :return: Original file path `fnm` with extension replaced by `ext`
    """
    return f'{os.path.splitext(fnm)[0]}.{ext}'


def log(s, c: str = 'log', c_time='green', as_str=False):
    """
    Prints `s` to console with color `c`
    """
    if not hasattr(log, 'reset'):
        log.reset = colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL
    if not hasattr(log, 'd'):
        log.d = dict(
            log='',
            warn=colorama.Fore.YELLOW,
            error=colorama.Fore.RED,
            err=colorama.Fore.RED,
            success=colorama.Fore.GREEN,
            suc=colorama.Fore.GREEN,
            info=colorama.Fore.BLUE,
            i=colorama.Fore.BLUE,
            w=colorama.Fore.RED,

            y=colorama.Fore.YELLOW,
            yellow=colorama.Fore.YELLOW,
            red=colorama.Fore.RED,
            r=colorama.Fore.RED,
            green=colorama.Fore.GREEN,
            g=colorama.Fore.GREEN,
            blue=colorama.Fore.BLUE,
            b=colorama.Fore.BLUE,

            m=colorama.Fore.MAGENTA
        )
    if c in log.d:
        c = log.d[c]
    if as_str:
        return f'{c}{s}{log.reset}'
    else:
        print(f'{c}{log(now(), c=c_time, as_str=True)}| {s}{log.reset}')


def log_s(s, c):
    return log(s, c=c, as_str=True)


def logi(s):
    """
    Syntactic sugar for logging `info` as string
    """
    return log_s(s, c='i')


def log_dict(d: Dict = None, with_color=True, **kwargs) -> str:
    """
    Syntactic sugar for logging dict with coloring for console output
    """
    if d is None:
        d = kwargs
    pairs = (f'{k}: {logi(v) if with_color else v}' for k, v in d.items())
    pref = log_s('{', c='m') if with_color else '{'
    post = log_s('}', c='m') if with_color else '}'
    return pref + ', '.join(pairs) + post


def hex2rgb(hx: str) -> Union[Tuple[int], Tuple[float]]:
    # Modified from https://stackoverflow.com/a/62083599/10732321
    if not hasattr(hex2rgb, 'regex'):
        hex2rgb.regex = re.compile(r'#[a-fA-F0-9]{3}(?:[a-fA-F0-9]{3})?$')
    m = hex2rgb.regex.match(hx)
    assert m is not None
    if len(hx) <= 4:
        return tuple(int(hx[i]*2, 16) for i in range(1, 4))
    else:
        return tuple(int(hx[i:i+2], 16) for i in range(1, 7, 2))


class MyTheme:
    """
    Theme based on `sty` and `Atom OneDark`
    """
    COLORS = OrderedDict([
        ('yellow', 'E5C07B'),
        ('green', '00BA8E'),
        ('blue', '61AFEF'),
        ('cyan', '2AA198'),
        ('red', 'E06C75'),
        ('purple', 'C678DD')
    ])
    yellow, green, blue, cyan, red, purple = (
        hex2rgb(f'#{h}') for h in ['E5C07B', '00BA8E', '61AFEF', '2AA198', 'E06C75', 'C678DD']
    )

    @staticmethod
    def set_color_type(t: str):
        """
        Sets the class attribute accordingly

        :param t: One of ['rgb`, `sty`]
            If `rgb`: 3-tuple of rgb values
            If `sty`: String for terminal styling prefix
        """
        for color, hex_ in MyTheme.COLORS.items():
            val = hex2rgb(f'#{hex_}')  # For `rgb`
            if t == 'sty':
                setattr(sty.fg, color, sty.Style(sty.RgbFg(*val)))
                val = getattr(sty.fg, color)
            setattr(MyTheme, color, val)


class MyFormatter(logging.Formatter):
    """
    Modified from https://stackoverflow.com/a/56944256/10732321

    Default styling: Time in green, metadata indicates severity, plain log message
    """
    RESET = sty.rs.fg + sty.rs.bg + sty.rs.ef

    MyTheme.set_color_type('sty')
    yellow, green, blue, cyan, red, purple = (
        MyTheme.yellow, MyTheme.green, MyTheme.blue, MyTheme.cyan, MyTheme.red, MyTheme.purple
    )

    KW_TIME = '%(asctime)s'
    KW_MSG = '%(message)s'
    KW_LINENO = '%(lineno)d'
    KW_FNM = '%(filename)s'
    KW_FUNCNM = '%(funcName)s'
    KW_NAME = '%(name)s'

    DEBUG = INFO = BASE = RESET
    WARN, ERR, CRIT = yellow, red, purple
    CRIT += sty.Style(sty.ef.bold)

    LVL_MAP = {  # level => (abbreviation, style)
        logging.DEBUG: ('DBG', DEBUG),
        logging.INFO: ('INFO', INFO),
        logging.WARNING: ('WARN', WARN),
        logging.ERROR: ('ERR', ERR),
        logging.CRITICAL: ('CRIT', CRIT)
    }

    def __init__(self, with_color=True, color_time=green):
        super().__init__()
        self.with_color = with_color

        sty_kw, reset = MyFormatter.blue, MyFormatter.RESET
        color_time = f'{color_time}{MyFormatter.KW_TIME}{sty_kw}| {reset}'

        def args2fmt(args_):
            if self.with_color:
                return color_time + self.fmt_meta(*args_) + f'{sty_kw} - {reset}{MyFormatter.KW_MSG}' + reset
            else:
                return f'{MyFormatter.KW_TIME}| {self.fmt_meta(*args_)} - {MyFormatter.KW_MSG}'

        self.formats = {level: args2fmt(args) for level, args in MyFormatter.LVL_MAP.items()}
        self.formatter = {
            lv: logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S') for lv, fmt in self.formats.items()
        }

    def fmt_meta(self, meta_abv, meta_style=None):
        if self.with_color:
            return f'{MyFormatter.purple}[{MyFormatter.KW_NAME}]' \
               f'{MyFormatter.blue}::{MyFormatter.purple}{MyFormatter.KW_FUNCNM}' \
               f'{MyFormatter.blue}::{MyFormatter.purple}{MyFormatter.KW_FNM}' \
               f'{MyFormatter.blue}:{MyFormatter.purple}{MyFormatter.KW_LINENO}' \
               f'{MyFormatter.blue}, {meta_style}{meta_abv}{MyFormatter.RESET}'
        else:
            return f'[{MyFormatter.KW_NAME}] {MyFormatter.KW_FUNCNM}::{MyFormatter.KW_FNM}' \
                   f':{MyFormatter.KW_LINENO}, {meta_abv}'

    def format(self, entry):
        return self.formatter[entry.levelno].format(entry)


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)  # For my own coloring
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(MyFormatter())
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    ic(now())
    ic(ch_ext('output/image-cloud, 2021-12-06 12:14:34, 1.png', 'pickle'))
