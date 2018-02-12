import logging
import subprocess as sp
import os
import pexpect
import re

log = logging.getLogger(__name__)

has_curl = sp.call(['which', 'curl'], stdout=sp.PIPE) == 0
has_wget = sp.call(['which', 'wget'], stdout=sp.PIPE) == 0

URL = 'http://mirror.ctan.org/systems/texlive/tlnet/'
OLDURL = 'ftp://tug.org/historic/systems/texlive/{v}/tlnet-final/'


def download(version=None, outdir='.'):
    os.makedirs(outdir, exist_ok=True)

    if version is None:
        url = URL + 'install-tl-unx.tar.gz'
    else:
        url = OLDURL.format(v=version) + 'install-tl-unx.tar.gz'

    if has_curl:
        log.info('Start downloading TeX Live {} using curl'.format(version or 'current'))
        download = sp.Popen(['curl', '-L', url], stdout=sp.PIPE, stderr=sp.PIPE)
    elif has_wget:
        log.info('Start downloading TeX Live {} using wget'.format(version or 'current'))
        download = sp.Popen(['wget', '-qO-', url], stdout=sp.PIPE, stderr=sp.PIPE)
    else:
        raise IOError('Either curl or wget required')

    sp.check_call(['tar', 'xz', '--directory', outdir], stdin=download.stdout)


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
