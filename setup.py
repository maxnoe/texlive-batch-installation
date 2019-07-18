from distutils.core import setup

setup(
    name='install_texlive',
    version='0.2.1',
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
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'install_texlive = install_texlive.__main__:main',
        ]
    },
)
