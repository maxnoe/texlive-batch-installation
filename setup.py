from distutils.core import setup

setup(
    name='install_texlive',
    version='0.1.0',
    description='Install texlive without human interaction in the process',
    url='http://github.com/maxnoe/texlive-batch-installation',
    author='Maximilian Noethe',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=[
        'install_texlive',
    ],
    install_requires=[
        'pexpect',
    ],
    entry_points={'console_scripts': ['install_texlive = install_texlive.__main__:main']},
)
