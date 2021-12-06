import os
from datetime import datetime

from icecream import ic


def now(as_str=True):
    d = datetime.now()
    return d.strftime('%Y-%m-%d %H:%M:%S') if as_str else d


def ch_ext(fnm, ext):
    """
    :return: Original file path `fnm` with extension replaced by `ext`
    """
    return f'{os.path.splitext(fnm)[0]}.{ext}'


if __name__ == '__main__':
    ic(now())
    ic(ch_ext('output/image-cloud, 2021-12-06 12:14:34, 1.png', 'pickle'))
