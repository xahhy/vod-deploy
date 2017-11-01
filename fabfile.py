from fabric import *
from fabric.context_managers import cd
from fabric.decorators import task
from fabric.operations import *
from fabric.state import env

env.hosts = ['192.168.1.105']
env.password = 'tongshi'

SOFTWARES = [
    'vim',
    'gnome-mplayer',
    'python-pip',
    'python3-pip',
]
PACKAGE_DIR = '/home/tongshi/Desktop/packages'


@task
def update_apt():
    sudo('apt update -y')
    sudo('apt upgrade -y')


@task
def install_software():
    software = ' '.join(SOFTWARES)
    sudo('apt-get install -y %s' % software)


@task
def copy_files():
    put(PACKAGE_DIR, '/home/tongshi/Desktop/')


@task
def install_ethernet():
    with settings(warn_only=True):
        with cd(PACKAGE_DIR):
            if run('test -d mlnx*').failed:
                run('tar xvf %s/mlnx*' % (PACKAGE_DIR))
            with cd('mlnx*'):
                if sudo('./install').succeeded:
                    sudo('/etc/init.d/mlnx-en.d restart')
