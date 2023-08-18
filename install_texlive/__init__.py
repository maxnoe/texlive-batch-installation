import logging
import os
import pexpect
import re
import requests
from io import BytesIO
import tarfile

__version__ = '0.3.2'

log = logging.getLogger(__name__)

URL = 'https://mirror.ctan.org/systems/texlive/tlnet/'
OLDURL = 'https://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/{v}/tlnet-final/'


def is_current(version):
    r = requests.get('https://tug.org/texlive/')
    r.raise_for_status()

    m = re.search(r'Current release: TeX Live ([0-9]{4})', r.text)
    if not m:
        raise ValueError('Could not determine current TeX Live version')

    current_version = int(m.groups()[0])
    log.debug('Current version of TeX Live is {}'.format(current_version))
    return current_version == version


def download(version=None, outdir='.'):
    os.makedirs(outdir, exist_ok=True)

    if version is None or is_current(version):
        url = URL + 'install-tl-unx.tar.gz'
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
