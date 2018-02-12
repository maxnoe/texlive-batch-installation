from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument(
    '-v', '--verbose', action='store_true', help='Create more verbose output'
)

parser.add_argument(
    '-t', '--texlive-version', dest='version',
    help='TeX Live version to install',
)

parser.add_argument(
    '--install-tl', dest='install_tl',
    help='Path to the install-tl script. If not given, TeX Live will be downloaded.',
)

parser.add_argument(
    '-k', '--keep-config', dest='keep', action='store_true',
    help='If an existing installation is found, keep its config',
)

parser.add_argument(
    '-p', '--prefix', dest='prefix',
    help='Installation prefix, equivalent to setting TEXLIVE_INSTALL_PREFIX'
)

parser.add_argument(
    '-c', '--collections', dest='collections',
    help=(
        'The TeX Live package collections to install.'
        ' E.g. -a to deselect all and only install the absolute basic TeX packages'
    )
)

parser.add_argument(
    '-s', '--scheme', dest='scheme', choices=set('abcdefghijk'),
    help='The TeX Live scheme to install. Default is "full"'
)

parser.add_argument(
    '-u', '--update', dest='update', action='store_true',
    help='Update TeX Live after installation is finished'
)

parser.add_argument(
    '-i', '--install', dest='install',
    help='Additional packages to install after the main Installation has finished'
)

parser.add_argument(
    '--source', action='store_true',
    help='Install the source tree',
)

parser.add_argument(
    '--docs', action='store_true',
    help='Install the docs tree',
)
