#!/usr/bin/python

import os
import sys
import subprocess
import shutil

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))
from charmhelpers.core import (
    hookenv,
    host,
)
from charmhelpers.fetch import apt_install, apt_update
from charmhelpers.contrib.charmsupport.nrpe import NRPE

from Config import Config


hooks = hookenv.Hooks()
conf = Config()
log = hookenv.log

required_pkgs = [
    'python-virtualenv',
    'python-pip',
    'logrotate',
]


# FIXME: Add some checks here
def configure_nrpe():
    return


# FIXME: This needs to be cached somehow so we know we're getting a working version
def install_devpi_server():
    log("CHARM: Installing devpi-server")
    venvdir = os.path.join(conf.mirror_userinfo().pw_dir, "venv")

    if not os.path.exists(venvdir):
        try:
            subprocess.check_call(["virtualenv", venvdir])
        except subprocess.CalledProcessError as e:
            log("CHARM: Error initialising virtualenv - {}".format(e))
            sys.exit(1)

    install_cmd = [os.path.join(venvdir, "bin", "pip"), "install", "-U", "devpi-server"]
    subprocess.check_call(install_cmd)
    return


# (Re)start the devpi server
def start_devpi_server():
    devpi_cmd = os.path.join(conf.mirror_userinfo().pw_dir, "venv", "local/bin/devpi-server")
    server_cmd = ["sudo", "-u", conf.mirror_user(), devpi_cmd]
    try:
        output = subprocess.check_output(server_cmd + ["--status"])
        if output.startswith("server is running"):
            subprocess.check_call(server_cmd + ["--stop"])
        if not conf.master():
            subprocess.check_call(server_cmd + ["--host=0.0.0.0", "--port=%d" % conf.port(), "--serverdir=%s" % conf.server_dir(), "--start"])
        else:
            subprocess.check_call(server_cmd + ["--master=%s" % conf.master(), "--host=0.0.0.0", "--port=%d" % conf.port(), "--serverdir=%s" % conf.server_dir(), "--start"])
    except subprocess.CalledProcessError as e:
        log("CHARM: Error restarting devpi-server - {}".format(e))


# Stop the devpi server
def stop_devpi_server():
    devpi_cmd = os.path.join(conf.mirror_userinfo().pw_dir, "venv", "local/bin/devpi-server")
    server_cmd = ["sudo", "-u", conf.mirror_user(), devpi_cmd]
    try:
        subprocess.check_call(server_cmd + ["--stop"])
    except subprocess.CalledProcessError as e:
        log("CHARM: Error stopping devpi-server - {}".format(e))


# FIXME: We should probably check if this changes and delete the old user if so
def create_mirror_user():
    try:
        mirror_userinfo = conf.mirror_userinfo()
    except KeyError:
        mirror_userinfo = host.adduser(conf.mirror_user(), system_user=True)
        host.mkdir(mirror_userinfo.pw_dir, owner=conf.mirror_user(), perms=0o755)


@hooks.hook("install")
def install():
    log("CHARM: Installing {}".format(conf.app_name()))
    apt_update()
    apt_install(required_pkgs, options=['--force-yes'])
    create_mirror_user()
    install_devpi_server()


@hooks.hook("config-changed")
def config_changed():
    log("CHARM: Configuring {}".format(conf.app_name()))
    create_mirror_user()

    # Set up the services
    configure_nrpe()

    # (Re)start the devpi server
    start_devpi_server()


@hooks.hook("upgrade-charm")
def upgrade_charm():
    log("CHARM: Upgrading {}".format(conf.app_name()))
    install()


@hooks.hook("start")
def start():
    log("CHARM: Starting {}".format(conf.app_name()))
    start_devpi_server()


@hooks.hook("stop")
def stop():
    log("CHARM: Stopping {}".format(conf.app_name()))
    stop_devpi_server()


@hooks.hook("nrpe-external-master-relation-changed")
def nrpe_external_master_relation_changed():
    log("CHARM: Changing nrpe relation for {}".format(conf.app_name()))
    configure_nrpe()


@hooks.hook("website-relation-joined")
def website_relation_joined():
    log("CHARM: Joining website relation for {}".format(conf.app_name()))
    hookenv.relation_set(hostname=hookenv.unit_private_ip(), port="3141")


if __name__ == "__main__":
    hook_name = os.path.basename(sys.argv[0])
    hooks.execute(sys.argv)
