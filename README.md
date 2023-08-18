# texlive batch install [![Build Status](https://travis-ci.org/MaxNoe/texlive-batch-installation.svg?branch=master)](https://travis-ci.org/MaxNoe/texlive-batch-installation)

The TeX Live installer does not allow for interaction-less installation.

This is the reason why I created this project using pexpect to talk to the `install-tl`
script.

Usage:
```
usage: install_texlive [-h] [-v] [-t VERSION] [--install-tl INSTALL_TL] [-k]
                       [-p PREFIX] [-c COLLECTIONS]
                       [-s {f,g,d,i,k,c,e,h,b,j,a}] [-u] [-i INSTALL]
                       [--source] [--docs]

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
  -s {f,g,d,i,k,c,e,h,b,j,a}, --scheme {f,g,d,i,k,c,e,h,b,j,a}
                        The TeX Live scheme to install. Default is "full"
  -u, --update          Update TeX Live after installation is finished
  -i INSTALL, --install INSTALL
                        Additional packages to install after the main
                        Installation has finished
  --source              Install the source tree
  --docs                Install the docs tree
```


For a minimal installation (e.g. for CI jobs building documents), it is recommended to
only install the bare minimum selection of package collections: `-c "-a"` and then
have a file `tex-packages.txt` with the actually needed packages to compile the document:

```
$ python -m install_texlive -p .texlive -t 2022 --collections='-a' --package-file tex-packages.txt --update
```

To find out which package provides which style file (e.g. to find out which CTAN package provides `scrartcl.cls`), this command is helpful:

```
$ tlmgr search --global --file '/scrartcl.cls'
koma-script:
	texmf-dist/tex/latex/koma-script/scrartcl.cls
```
