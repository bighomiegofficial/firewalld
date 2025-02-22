# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright (C) 2011-2016 Red Hat, Inc.
#
# Authors:
# Thomas Woerner <twoerner@redhat.com>

from firewall import config
from firewall.core.logger import log
from firewall.core.io.lockdown_whitelist import LockdownWhitelist
from firewall import errors
from firewall.errors import FirewallError

class FirewallPolicies:
    def __init__(self):
        self._lockdown = False
        self.lockdown_whitelist = LockdownWhitelist(config.LOCKDOWN_WHITELIST)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__, self._lockdown,
                                           self.lockdown_whitelist)

    def cleanup(self):
        self._lockdown = False
        self.lockdown_whitelist.cleanup()

    # lockdown

    def access_check(self, key, value):
        if key == "context":
            log.debug2('Doing access check for context "%s"' % value)
            if self.lockdown_whitelist.match_context(value):
                log.debug3('context matches.')
                return True
        elif key == "uid":
            log.debug2('Doing access check for uid %d' % value)
            if self.lockdown_whitelist.match_uid(value):
                log.debug3('uid matches.')
                return True
        elif key == "user":
            log.debug2('Doing access check for user "%s"' % value)
            if self.lockdown_whitelist.match_user(value):
                log.debug3('user matches.')
                return True
        elif key == "command":
            log.debug2('Doing access check for command "%s"' % value)
            if self.lockdown_whitelist.match_command(value):
                log.debug3('command matches.')
                return True
        return False

    def enable_lockdown(self):
        if self._lockdown:
            raise FirewallError(errors.ALREADY_ENABLED, "enable_lockdown()")
        self._lockdown = True

    def disable_lockdown(self):
        if not self._lockdown:
            raise FirewallError(errors.NOT_ENABLED, "disable_lockdown()")
        self._lockdown = False

    def query_lockdown(self):
        return self._lockdown
