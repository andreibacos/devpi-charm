#!/usr/bin/python
#
# Copyright 2015 Canonical Ltd.  All rights reserved
# Author: Chris Stratford <chris.stratford@canonical.com>

import os
import sys
import pwd

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))
from charmhelpers.core.hookenv import config, log


class Config:
    def app_name(self):
        return "pypi-mirror"

    def mirror_user(self):
        return str(config("mirror_user"))

    def mirror_userinfo(self):
        try:
            mirror_userinfo = pwd.getpwnam(self.mirror_user())
        except KeyError:
            log("CHARM: mirror user '{}' has not been created".format(self.mirror_user()))
            raise KeyError
        return mirror_userinfo
