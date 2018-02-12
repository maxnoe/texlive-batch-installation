import pexpect
from glob import glob
import os
import sys
import logging
import tempfile
import re
import subprocess as sp

from . import command, download, OLDURL
from .parser import parser


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('install_texlive')

timeout = 30


def main():
    args = parser.parse_args()

    if args.verbose:
        log.level = logging.DEBUG

    if args.prefix:
        args.prefix = os.path.abspath(args.prefix)
        os.environ['TEXLIVE_INSTALL_PREFIX'] = args.prefix
        os.makedirs(args.prefix, exist_ok=True)

    log.info('Installing texlive to {}'.format(args.prefix or '/usr/local/texlive'))

    if args.install_tl:
        install_script = args.install_tl
        cmd = install_script
    else:
        directory = os.path.join(
            tempfile.gettempdir(), 'texlive-' + (args.version or 'current')
        )
        download(version=args.version, outdir=directory)
        install_script = glob(os.path.join(directory, 'install-tl-*/install-tl'))[-1]

        if args.version is None:
            cmd = install_script
        else:
            cmd = install_script + ' --repository=' + OLDURL.format(v=args.version)

    log.info(cmd)

    tl = pexpect.spawn(cmd, timeout=timeout)

    try:
        command(tl, 'installation.profile', 'N', timeout=5)
    except pexpect.TIMEOUT:
        pass

    try:
        command(tl, 'Import settings', 'y' if args.keep else 'n', timeout=5)
    except pexpect.TIMEOUT:
        log.info('No previous installation found')

    try:
        if args.scheme:
            command(tl, 'Enter command:', 'S', timeout=timeout)
            command(tl, 'Enter letter', args.scheme,  timeout=timeout)
            command(tl, 'Enter letter', 'R',  timeout=timeout)

        if args.collections:
            command(tl, 'Enter command:', 'C', timeout=timeout)
            command(tl, 'Enter letter', args.collections,  timeout=timeout)
            command(tl, 'Enter letter', 'R',  timeout=timeout)

        command(tl, 'Enter command:', 'I', timeout=timeout)
        log.info('Starting installation')
    except pexpect.TIMEOUT:
        print('Something went wrong')
        sys.exit(1)

    lines = ''
    try:
        while not tl.terminated:
            line = tl.readline().decode()
            log.debug(line.strip())
            lines += line
    except pexpect.EOF:
        log.error('EOF')

    tl.close()
    if tl.exitstatus == 0:
        log.info('Installation installed succesfully')
    else:
        log.error('Installation did not finish succesfully')
        sys.exit(tl.exitstatus)

    bindir = re.findall(r'Most importantly, add\s+(.*)\s+to your PATH', lines)[0].strip()
    version = re.findall(r'20[0-9][0-9]', bindir)[0]
    env = os.environ
    env['PATH'] = os.path.abspath(bindir) + ':' + env['PATH']

    if version != '2017':
        sp.Popen(
            ['tlmgr', 'option', 'repository', OLDURL.format(v=version)],
            env=env
        ).wait()

    if args.update:
        log.info('Start updating')
        sp.Popen(
            ['tlmgr', 'update', '--self', '--all', '--reinstall-forcibly-removed'],
            env=env,
        ).wait()
        log.info('Finished')

    if args.install:
        log.info('Start installing addtional packages')
        sp.Popen(['tlmgr', 'install', args.install], env=env).wait()
        log.info('Finished')


if __name__ == '__main__':
    main()
