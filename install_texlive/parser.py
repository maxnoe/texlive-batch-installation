from argparse import ArgumentParser
from . import __version__

parser = ArgumentParser(prog='install_texlive')

parser.add_argument('-V', '--version', action='version', version=__version__)

parser.add_argument(
    '-v', '--verbose', action='store_true', help='Create more verbose output'
)

parser.add_argument(
    '-t', '--texlive-version', dest='version', type=int,
    help='TeX Live version to install',
)

parser.add_argument(
    '--install-tl',
    help='Path to the install-tl script. If not given, TeX Live will be downloaded.',
)

parser.add_argument(
    '-k', '--keep-config', action='store_true',
    help='If an existing installation is found, keep its config',
)

parser.add_argument(
    '-p', '--prefix',
    help='Installation prefix, equivalent to setting TEXLIVE_INSTALL_PREFIX'
)

parser.add_argument(
    '-c', '--collections',
    help=(
        'The TeX Live package collections to install.'
        ' E.g. -a to deselect all and only install the absolute basic TeX packages'
    )
)

parser.add_argument(
    '-s', '--scheme', choices=set('abcdefghijk'),
    help='The TeX Live scheme to install. Default is "full"'
)

parser.add_argument(
    '-u', '--update', action='store_true',
    help='Update TeX Live after installation is finished'
)

parser.add_argument(
    '-i', '--install',
    help='Additional packages to install after the main Installation has finished as comma separated list'
)

parser.add_argument(
    '-f', '--package-file',
    help='A file with one package per line to be install after the main installation has finished'
)

parser.add_argument(
    '--source', action='store_true',
    help='Install the source tree',
)

parser.add_argument(
    '--docs', action='store_true',
    help='Install the docs tree',
)

parser.add_argument(
    "-r", "--repository",
    help="If given, set ctan mirror to this URL.",
)
