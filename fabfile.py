# coding:utf8
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
    'mysql'
]
PACKAGE_DIR = '/home/tongshi/Desktop/packages'


@task
def install(text):
    """通过命令行使用apt-get安装软件,fab install:xxxx"""
    sudo('apt-get install -y %s' % text)


@task
def update_apt():
    """安装完Ubuntu系统后更新apt仓库"""
    sudo('apt update -y')
    sudo('apt upgrade -y')


@task
def install_software():
    """使用apt-get安装SOFTWARE列表中的软件"""
    software = ' '.join(SOFTWARES)
    sudo('apt-get install -y %s' % software)


@task
def copy_files():
    """拷贝安装包"""
    put(PACKAGE_DIR, '/home/tongshi/Desktop/')


@task
def install_ethernet():
    """安装万兆网卡驱动"""
    with settings(warn_only=True):
        with cd(PACKAGE_DIR):
            if run('test -d mlnx*').failed:
                run('tar xvf %s/mlnx*' % (PACKAGE_DIR))
            with cd('mlnx*'):
                if sudo('./install').succeeded:
                    sudo('/etc/init.d/mlnx-en.d restart')
