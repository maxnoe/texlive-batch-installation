import logging
import os
import pexpect
import re
import requests
from io import BytesIO
import tarfile
from functools import lru_cache
from io import StringIO
from html.parser import HTMLParser
from ._version import __version__, __version_tuple__


__all__ = [
    "__version__",
    "__version_tuple__",
    "command",
    "download",
    "get_mirror",
    "get_size",
    "is_current",
    "URL",
    "OLDURL",
]


log = logging.getLogger(__name__)

URL = 'https://mirror.ctan.org/systems/texlive/tlnet/'
OLDURL = 'https://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/{v}/tlnet-final/'


class GetText(HTMLParser):
    """Only extract text of html page"""

    def __init__(self):
        super().__init__()
        self._text = StringIO()

    def handle_data(self, d):
        self._text.write(d)

    @property
    def text(self):
        return self._text.getvalue()


@lru_cache
def is_current(version):
    r = requests.get('https://tug.org/texlive/')
    r.raise_for_status()

    parser = GetText()
    parser.feed(r.text)

    m = re.search(r'Current release: TeX Live ([0-9]{4})', parser.text)
    if not m:
        raise ValueError('Could not determine current TeX Live version')

    current_version = int(m.groups()[0])
    log.debug('Current version of TeX Live is {}'.format(current_version))
    return current_version == version


def get_mirror():
    """Get a CTAN mirror"""
    r = requests.get(URL, allow_redirects=False)
    r.raise_for_status()
    return r.headers["Location"]


def download(version=None, outdir='.', url=None):
    os.makedirs(outdir, exist_ok=True)

    if version is None or is_current(version):
        url = url or URL
        url = url.rstrip("/") + '/install-tl-unx.tar.gz'
    else:
        url = OLDURL.format(v=version) + 'install-tl-unx.tar.gz'

    log.debug('Downloading from {}'.format(url))

    ret = requests.get(url)
    ret.raise_for_status()

    tar = tarfile.open(fileobj=BytesIO(ret.content), mode='r:gz')
    tar.extractall(outdir)


def command(process, pattern, send, **kwargs):
    process.expect(pattern, **kwargs)
    process.sendline(send)


def get_size(process):
    timeout = process.timeout
    process.timeout = 1
    lines = ''
    try:
        while True:
            lines += process.readline().decode()
    except pexpect.TIMEOUT:
        pass

    size = re.findall(r'disk space required: ([0-9]+ MB)', lines)[-1]
    process.timeout = timeout
    return size
