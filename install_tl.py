import pexpect
from glob import glob
import os


if __name__ == '__main__':
    install_script = glob('install-tl-*/install-tl')

    os.environ['TEXLIVE_INSTALL_PREFIX'] = '/home/travis/texlive'
    child = pexpect.spawn(install_script)

    try:
        child.expect('Import settings from previous TeX Live installation', timeout=10)
        print(child.before.decode())
        print(child.after.decode())
        child.sendline('n')
    except pexpect.TIMEOUT:
        print('No previous installation found')

    try:
        child.expect('Enter command:', timeout=10)
        print(child.before.decode())
        print(child.after.decode())
        child.sendline('I')
    except pexpect.TIMEOUT:
        print('Something went wrong')

    try:
        while True:
            try:
                print(child.readline().decode().strip())
            except pexpect.TIMEOUT:
                pass
    except pexpect.EOF:
        print('Installation seems to be finished')
