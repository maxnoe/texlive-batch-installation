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
