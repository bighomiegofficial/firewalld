#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright (C) 2012 Red Hat, Inc.
#
# Authors:
# Thomas Woerner <twoerner@redhat.com>
# Jiri Popelka <jpopelka@redhat.com>

# To use in git tree: PYTHONPATH=.. python firewalld-test.py

import dbus
import sys
import unittest

from firewall import config
from firewall.dbus_utils import dbus_to_python

class TestFirewallDInterfaceDirect(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        bus = dbus.SystemBus()
        dbus_obj = bus.get_object(config.dbus.DBUS_INTERFACE,
                                  config.dbus.DBUS_PATH)
        dbus_obj_config = bus.get_object(config.dbus.DBUS_INTERFACE,
                                         config.dbus.DBUS_PATH_CONFIG)
        self.fw = dbus.Interface(dbus_obj,
                                 dbus_interface=config.dbus.DBUS_INTERFACE)
        self.fw_direct = dbus.Interface(
            dbus_obj, dbus_interface=config.dbus.DBUS_INTERFACE_DIRECT)
        self.config_properties = dbus.Interface(dbus_obj_config,
                                    dbus_interface='org.freedesktop.DBus.Properties')
        self.config_properties.Set(config.dbus.DBUS_INTERFACE_CONFIG, "FlushAllOnReload", "no")
        self.fw.reload()
        # always have "direct_foo1" available
        self.fw_direct.addChain("ipv4", "filter", "direct_foo1")

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.fw_direct.removeChain("ipv4", "filter", "direct_foo1")

    def test_add_removeChain(self):
        self.fw_direct.addChain("ipv4", "filter", "direct_foo2")
        # Re-adding
        self.assertRaisesRegex(Exception, 'ALREADY_ENABLED',
                                self.fw_direct.addChain, "ipv4", "filter", "direct_foo2")
        ret = self.fw_direct.getChains("ipv4", "filter")
        self.assertTrue(len(ret)==2) # "direct_foo1" and "direct_foo2"
        #pprint (dbus_to_python(ret))
        ret = self.fw_direct.queryChain("ipv4", "filter", "direct_foo2")
        self.assertTrue(dbus_to_python(ret))

        self.fw_direct.removeChain("ipv4", "filter", "direct_foo2")
        # Re-removing
        self.assertRaisesRegex(Exception, 'NOT_ENABLED',
                                self.fw_direct.removeChain, "ipv4", "filter", "direct_foo2")
        ret = self.fw_direct.getChains("ipv4", "filter")
        self.assertTrue(len(ret)==1) # "direct_foo1"
        ret = self.fw_direct.queryChain("ipv4", "filter", "direct_foo2")
        self.assertFalse(dbus_to_python(ret))

    def test_add_removeRule(self):
        self.fw_direct.addRule("ipv4", "filter", "direct_foo1", 0, [ "-m", "tcp", "-p", "tcp", "--dport", "332", "-j", "ACCEPT" ])
        self.fw_direct.addRule("ipv4", "filter", "direct_foo1", 0, [ "-m", "tcp", "-p", "tcp", "--dport", "333", "-j", "ACCEPT" ])
        self.fw_direct.addRule("ipv4", "filter", "direct_foo1", 1, [ "-m", "tcp", "-p", "tcp", "--dport", "334", "-j", "ACCEPT" ])
        self.fw_direct.addRule("ipv4", "filter", "direct_foo1", -5, [ "-m", "tcp", "-p", "tcp", "--dport", "331", "-j", "ACCEPT" ])
        self.fw_direct.addRule("ipv4", "filter", "direct_foo1", -10, [ "-m", "tcp", "-p", "tcp", "--dport", "330", "-j", "ACCEPT" ])
        self.fw_direct.addRule("ipv4", "filter", "direct_foo1", -5, [ "-m", "udp", "-p", "udp", "--dport", "331", "-j", "ACCEPT" ])
        # Re-adding
        self.assertRaisesRegex(Exception, 'ALREADY_ENABLED',
                                self.fw_direct.addRule, "ipv4", "filter", "direct_foo1", -5, [ "-m", "udp", "-p", "udp", "--dport", "331", "-j", "ACCEPT" ])
        ret = self.fw_direct.queryRule("ipv4", "filter", "direct_foo1", -5, [ "-m", "udp", "-p", "udp", "--dport", "331", "-j", "ACCEPT" ])
        self.assertTrue(dbus_to_python(ret))
        ret = self.fw_direct.getRules("ipv4", "filter", "direct_foo1")
        self.assertTrue(len(ret) == 6)
        #pprint (dbus_to_python(ret))

        self.fw_direct.removeRule("ipv4", "filter", "direct_foo1", -10, [ "-m", "tcp", "-p", "tcp", "--dport", "330", "-j", "ACCEPT" ])
        self.fw_direct.removeRule("ipv4", "filter", "direct_foo1", -5, [ "-m", "tcp", "-p", "tcp", "--dport", "331", "-j", "ACCEPT" ])
        self.fw_direct.removeRule("ipv4", "filter", "direct_foo1", -5, [ "-m", "udp", "-p", "udp", "--dport", "331", "-j", "ACCEPT" ])
        self.fw_direct.removeRule("ipv4", "filter", "direct_foo1", 0, [ "-m", "tcp", "-p", "tcp", "--dport", "332", "-j", "ACCEPT" ])
        self.fw_direct.removeRule("ipv4", "filter", "direct_foo1", 0, [ "-m", "tcp", "-p", "tcp", "--dport", "333", "-j", "ACCEPT" ])
        self.fw_direct.removeRule("ipv4", "filter", "direct_foo1", 1, [ "-m", "tcp", "-p", "tcp", "--dport", "334", "-j", "ACCEPT" ])
        # Re-removing
        self.assertRaisesRegex(Exception, 'NOT_ENABLED',
                                self.fw_direct.removeRule, "ipv4", "filter", "direct_foo1", 1, [ "-m", "tcp", "-p", "tcp", "--dport", "334", "-j", "ACCEPT" ])
        ret = self.fw_direct.queryRule("ipv4", "filter", "direct_foo1", 1, [ "-m", "tcp", "-p", "tcp", "--dport", "334", "-j", "ACCEPT" ])
        self.assertFalse(dbus_to_python(ret))
        ret = self.fw_direct.getRules("ipv4", "filter", "direct_foo1")
        self.assertTrue(ret == [])

    def test_passthrough(self):
        self.fw_direct.passthrough("ipv4", [ "-t", "filter", "-N", "foobar" ])
        #fw_direct.passthrough("ipv4", [ "-t", "filter", "-L" ])

    def test_reload(self):
        self.fw.reload()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFirewallDInterfaceDirect)
    results = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if results.wasSuccessful() else 1)
