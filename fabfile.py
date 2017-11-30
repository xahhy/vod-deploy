# coding:utf8
from fabric import *
from fabric.context_managers import cd
from fabric.contrib.project import rsync_project, upload_project
from fabric.decorators import task
from fabric.operations import *
from fabric.state import env
from fabric.tasks import execute

env.hosts = ['192.168.1.104']
env.password = 'tongshi'

# 不要在这里安装mysql
SOFTWARES = [
    'vim',
    'gnome-mplayer',
    'python-pip',
    'python3-pip',
    'nginx',
    'git',
    'ntp'
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


@task
def optimize_server():
    """优化服务器吞吐量设置"""
    with settings(warn_only=True):
        result = run('grep file-max /etc/sysctl.conf')
        if 'fs.file-max' not in result:
            sudo('echo "fs.file-max = 131072" >> /etc/sysctl.conf')
        sudo('sysctl -p')

        # 更改/etc/security/limits.conf
        LIMITS_CONF = '*    soft    nproc    131072\n' \
                      '*    hard    nproc    131072\n' \
                      '*    soft    nofile    131072\n' \
                      '*    hard    nofile    131072\n' \
                      'root    soft    nproc    131072\n' \
                      'root    hard    nproc    131072\n' \
                      'root    soft    nofile    131072\n' \
                      'root    hard    nofile    131072'
        result = run('cat /etc/security/limits.conf')
        if LIMITS_CONF not in result.replace('\r', ''):  # 返回的结果竟然包含\r
            sudo('echo "%s" >> /etc/security/limits.conf' % LIMITS_CONF)

        # 更改/etc/pam.d/common-session
        COMMON_SESSION = 'session   required    pam_limits.so'
        result = run('cat /etc/pam.d/common-session')
        if COMMON_SESSION not in result:
            sudo('echo "%s" >> /etc/pam.d/common-session' % COMMON_SESSION)


@task
def deploy():
    """部署点播Django服务以及点播网页"""
    sudo('mkdir -p /home/share & chmod 777 /home/share')
    code_dir = '/home/share/vod'
    with settings(warn_only=True):
        # if run('test -d %s' % code_dir).failed:
        #     run('git clone https://github.com/xahhy/Django-vod.git /home/share/vod')
        # with cd(code_dir):
        #     run('git pull')
        rsync_project('/home/share/vod/', local_dir='/home/share/vod/',extra_opts='-l')
            #upload_project(remote_dir='/home/share/vod/', local_dir='/home/share/vod/env')
        rsync_project('/home/share/vod-html/', local_dir='/home/share/vod-html/', extra_opts='-l')
        sudo('ln -s /home/share/vod-html /var/www/html/vod')


@task
def mysql_conf():
    """配置数据库,允许远程登录"""
    sudo('sed -ie \'s/127\.0\.0\.1/0\.0\.0\.0/\' /etc/mysql/mysql.conf.d/mysqld.cnf')
    AUTH_SQL = """GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '123' WITH GRANT OPTION;FLUSH PRIVILEGES;"""
    run('mysql -uroot -p123 -e"%s"' % AUTH_SQL)
    sudo('service mysql restart')


@task
def nginx_conf():
    """配置Nginx"""
    put('/etc/nginx/sites-available/vod', '/etc/nginx/sites-available/', use_sudo=True)
    put('/etc/nginx/sites-enabled/vod', '/etc/nginx/sites-enabled/', use_sudo=True)
    sudo('service nginx -s reload')


@task
def install_nginx():
    with cd('/home/tongshi/Downloads'):
        run('wget http://nginx.org/keys/nginx_signing.key')
        sudo('apt-key add nginx_signing.key')
    sudo('echo "deb http://nginx.org/packages/ubuntu/ xenial nginx" >> /etc/apt/sources.list')
    sudo('echo "deb-src http://nginx.org/packages/ubuntu/ xenial nginx" >> /etc/apt/sources.list')
    sudo('apt-get update')
    sudo('apt-get install nginx -y')


@task
def init_dev():
    execute(update_apt)
    execute(copy_files)
    # execute(install_ethernet)
    execute(install_software)
    execute(install_nginx)
    execute(optimize_server)


if __name__ == '__main__':
    execute(optimize_server)
