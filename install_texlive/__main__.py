import pexpect
from glob import glob
import os
import sys
import logging
import tempfile
import shutil
import re
import subprocess as sp

from . import command, download, URL, OLDURL, get_size, is_current
from .parser import parser


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('install_texlive')


def main(timeout=3600):
    args = parser.parse_args()

    if args.verbose:
        log.level = logging.DEBUG

    if args.install_tl:
        install_script = args.install_tl
        cmd = install_script
    else:
        directory = os.path.join(
            tempfile.gettempdir(), 'texlive-{}'.format(args.version or 'current')
        )
        download(version=args.version, outdir=directory)
        install_script = glob(os.path.join(directory, 'install-tl-*/install-tl'))[-1]

        if args.version is None or is_current(args.version):
            cmd = install_script
        else:
            cmd = install_script + ' --repository=' + OLDURL.format(v=args.version)

    while True:
        log.info('Install texlive')

        tl = pexpect.spawn(cmd, timeout=timeout)

        if args.prefix:
            args.prefix = os.path.abspath(args.prefix)
            os.environ['TEXLIVE_INSTALL_PREFIX'] = args.prefix
            os.makedirs(args.prefix, exist_ok=True)

        log.info('Installing texlive to {}'.format(args.prefix or '/usr/local/texlive'))
        log.info(cmd)

        try:
            command(tl, 'installation.profile', 'N', timeout=5)
        except pexpect.TIMEOUT:
            log.info('No installation profile')
        except pexpect.exceptions.EOF:
            log.error('Wrong URL, restart installation')
            tl.close()
            timeout += 100
            continue

        try:
            command(tl, 'Import settings', 'y' if args.keep_config else 'n',
                    timeout=5)
        except pexpect.TIMEOUT:
            log.info('No previous installation found')
        except pexpect.exceptions.EOF:
            log.error('Wrong URL, restart installation')
            tl.close()
            timeout += 100
            continue

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
            log.error('Something went wrong, install time out')
            tl.close()
            shutil.rmtree(args.prefix)
            timeout += 100
            continue
        except pexpect.exceptions.EOF:
            log.error('Wrong URL, restart installation')
            tl.close()
            shutil.rmtree(args.prefix)
            timeout += 100
            continue

        lines = ''
        try:
            while not tl.terminated:
                line = tl.readline().decode()
                log.debug(line.strip())
                lines += line
        except pexpect.EOF:
            log.error('line EOF')
            tl.close()
            shutil.rmtree(args.prefix)
            timeout += 100
            continue
        except pexpect.TIMEOUT:
            log.error('Something went wrong, readline time out')
            tl.close()
            shutil.rmtree(args.prefix)
            timeout += 100
            continue
        except pexpect.exceptions.EOF:
            log.error('line EOF')
            tl.close()
            shutil.rmtree(args.prefix)
            timeout += 100
            continue

        tl.close()
        if tl.exitstatus == 0:
            log.info('Installation installed succesfully')
        else:
            log.error('Installation did not finish succesfully')
            tl.close()
            shutil.rmtree(args.prefix)
            timeout += 100
            continue

        bindir = re.findall(r'Most importantly, add\s+(.*)\s+to your PATH', lines)[0].strip()
        version = re.findall(r'20[0-9][0-9]', bindir)[0]
        env = os.environ
        env['PATH'] = os.path.abspath(bindir) + ':' + env['PATH']

        if args.version is not None and not is_current(args.version):
            repo = OLDURL.format(v=version)
        else:
            repo = URL
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
            log.info('Start installing addtional packages')
            # tlmgr must always be up to date to install packages
            sp.run(['tlmgr', 'update', '--self'], env=env, check=True)
            sp.run(['tlmgr', 'install', *additional_packages], env=env, check=True)
            log.info('Finished')

        if args.link:
            linkpath = '{}'.format(args.prefix or '/usr/local/texlive') + '/bin'
            try:
                os.symlink(bindir, linkpath)
            except FileExistsError:
                os.remove(linkpath)
                os.symlink(bindir, linkpath)
            finally:
                log.info('Link finished')
        break


if __name__ == '__main__':
    main()
