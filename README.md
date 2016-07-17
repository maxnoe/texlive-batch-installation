# texlive batch install [![Build Status](https://travis-ci.org/MaxNoe/texlive-batch-installation.svg?branch=master)](https://travis-ci.org/MaxNoe/texlive-batch-installation)

The TeX Live installer does not allow for interaction less installation.
This is the reason why I created this project using pexpect to talk to the `install-tl`
script.

Usage:
```
install_texlive [-h] [-v] [-t VERSION] [--install-tl INSTALL_TL] [-k]
                       [-p PREFIX] [-c COLLECTIONS]
                       [-s {d,i,e,j,c,g,b,f,a,h,k}]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Create more verbose output
  -t VERSION, --texlive-version VERSION
                        TeX Live version to install
  --install-tl INSTALL_TL
                        Path to the install-tl script. If not given, TeX Live
                        will be downloaded.
  -k, --keep-config     If an existing installation is found, keep its config
  -p PREFIX, --prefix PREFIX
                        Installation prefix, equivalent to setting
                        TEXLIVE_INSTALL_PREFIX
  -c COLLECTIONS, --collections COLLECTIONS
                        The TeX Live package collections to install. E.g. -a
                        to deselect all and only install the absolute basic
                        TeX packages
  -s {d,i,e,j,c,g,b,f,a,h,k}, --scheme {d,i,e,j,c,g,b,f,a,h,k}
                        The TeX Live scheme to install. Default is "full" (a)
```
