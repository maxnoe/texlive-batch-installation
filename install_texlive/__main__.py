import pexpect
from glob import glob
import os
import sys
import logging
import tempfile
import re
import subprocess as sp

from . import command, download, OLDURL, URL, get_size, is_current, get_mirror
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

    os.environ["TEXLIVE_INSTALL_ENV_NOCHECK"] = "1"
    log.info('Installing texlive to {}'.format(args.prefix or '/usr/local/texlive'))

    reset_repository = False
    if args.repository is None:
        if args.version is None or is_current(args.version):
            args.repository = get_mirror()
            reset_repository = True
        else:
            args.repository = OLDURL.format(v=args.version)

    if args.install_tl:
        install_script = args.install_tl
        cmd = install_script
    else:
        log.info("Using repository: %s", args.repository)
        directory = os.path.join(
            tempfile.gettempdir(), 'texlive-{}'.format(args.version or 'current')
        )
        download(version=args.version, outdir=directory, url=args.repository)
        install_script = glob(os.path.join(directory, 'install-tl-*/install-tl'))[-1]
        cmd = install_script + ' --repository={}'.format(args.repository) 

    log.info(cmd)

    tl = pexpect.spawn(cmd, timeout=timeout)

    try:
        command(tl, 'installation.profile', 'N', timeout=5)
    except pexpect.TIMEOUT:
        pass

    try:
        command(tl, 'Import settings', 'y' if args.keep_config else 'n', timeout=5)
    except pexpect.TIMEOUT:
        log.info('No previous installation found')

    try:
        if args.scheme:
            command(tl, 'Enter command:', 'S', timeout=timeout)
            command(tl, 'Enter letter', args.scheme, timeout=timeout)
            command(tl, 'Enter letter', 'R', timeout=timeout)

        if args.collections:
            command(tl, 'Enter command:', 'C', timeout=timeout)
            command(tl, 'Enter letter', args.collections, timeout=timeout)
            command(tl, 'Enter letter', 'R', timeout=timeout)

        if not args.docs:
            command(tl, 'Enter command:', 'O', timeout=timeout)
            command(tl, 'Enter command:', 'D', timeout=timeout)
            command(tl, 'Enter command:', 'R', timeout=timeout)

        if not args.source:
            command(tl, 'Enter command:', 'O', timeout=timeout)
            command(tl, 'Enter command:', 'S', timeout=timeout)
            command(tl, 'Enter command:', 'R', timeout=timeout)

        log.info('Installation size will be {}'.format(get_size(tl)))
        log.info('Starting installation')
        command(tl, 'Enter command:', 'I', timeout=timeout)
    except pexpect.TIMEOUT:
        log.error('Something went wrong')
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

    repo = args.repository
    if args.version is not None and not is_current(args.version):
        repo = OLDURL.format(v=version)

    if repo is not None:
        log.info("Setting repository to %s", repo)
        sp.run(
            ['tlmgr', 'option', 'repository', repo],
            env=env,
            check=True,
        )

    if args.update:
        log.info('Start updating')
        sp.run(
            ['tlmgr', 'update', '--self', '--all', '--reinstall-forcibly-removed'],
            env=env,
            check=True,
        )
        log.info('Finished')

    additional_packages = []
    if args.install:
        additional_packages.extend(args.install.split(','))

    if args.package_file:
        with open(args.package_file, 'r') as f:
            additional_packages.extend(f.read().splitlines())

    if additional_packages:
        log.info('Start installing additional packages')
        # tlmgr must always be up to date to install packages
        sp.run(['tlmgr', 'update', '--self'], env=env, check=True)
        sp.run(['tlmgr', 'install', *additional_packages], env=env, check=True)
        log.info('Finished')

    if reset_repository:
        log.info("Resetting repository to default CTAN mirror")
        sp.run(['tlmgr', 'option', 'repository', URL])


if __name__ == '__main__':
    main()
