import pexpect
from glob import glob
import os
import sys
import logging
import tempfile

from . import command, download, OLDURL
from .parser import parser


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('install_texlive')


def main():
    args = parser.parse_args()

    if args.verbose:
        log.level = logging.DEBUG

    if args.prefix:
        os.environ['TEXLIVE_INSTALL_PREFIX'] = args.prefix
        os.makedirs(args.prefix, exist_ok=True)

    if args.install_tl:
        install_script = args.install_tl
    else:
        directory = os.path.join(tempfile.gettempdir(), args.version or 'current')
        download(version=args.version, outdir=directory)
        install_script = glob(os.path.join(directory, 'install-tl-*/install-tl'))[-1]

    if args.version is None:
        cmd = install_script
    else:
        cmd = install_script + ' --repository=' + OLDURL.format(v=args.version)

    print(cmd)

    tl = pexpect.spawn(cmd)

    try:
        command(tl, 'installation.profile', 'N', timeout=10)
    except pexpect.TIMEOUT:
        pass

    try:
        command(tl, 'Import settings', 'y' if args.keep else 'n', timeout=10)
    except pexpect.TIMEOUT:
        log.info('No previous installation found')

    try:
        #  command('Enter command:', 'C', timeout=10)
        #  command('Enter letter', '-acfghkyIKLMSW',  timeout=10)
        #  command('Enter letter', 'R',  timeout=10)
        command(tl, 'Enter command:', 'I', timeout=10)
        log.info('Starting installation')
    except pexpect.TIMEOUT:
        print('Something went wrong')
        sys.exit(1)

    try:
        while not tl.terminated:
            log.debug(tl.readline().decode().strip())
    except pexpect.EOF:
        log.info('Installation seems to be finished')

    tl.close()
    sys.exit(tl.exitstatus)


if __name__ == '__main__':
    main()
