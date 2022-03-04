import urllib.request


from icecream import ic


def download_str(url, write=True):
    fnm = url.split('/')[-1]
    # ic(fnm)
    res = urllib.request.urlopen(url)
    txt = res.read().decode('utf-8')
    with open(fnm, 'w') as f:
        f.write(txt)
    # ic(text)


if __name__ == '__main__':
    url = 'https://huggingface.co/front/assets/huggingface_logo-noborder.svg'

    download_str(url)
