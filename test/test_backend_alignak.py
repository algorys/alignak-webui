#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015:
#   Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
# import the unit testing module

import os
import json
import time
import shlex
import unittest2
import subprocess

from nose import with_setup
from nose.tools import *

from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT
from alignak_webui.objects.backend import BackendConnection

pid = None
backend_address = "http://127.0.0.1:5000/"
# backend_address = "http://94.76.229.155:80"


def setup_module(module):
    print ("")
    print ("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['TEST_ALIGNAK_BACKEND_DB'] = 'alignak-backend'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split('mongo %s --eval "db.dropDatabase()"' % os.environ['TEST_ALIGNAK_BACKEND_DB'])
        )
        assert exit_code == 0
        time.sleep(1)

        # No console output for the applications backend ...
        pid = subprocess.Popen(
            shlex.split('alignak_backend')
        )
        print ("PID: %s" % pid)
        time.sleep(3)

        print ("")
        print ("populate backend content")
        exit_code = subprocess.call(
            shlex.split('alignak_backend_import --delete cfg/default/_main.cfg')
        )
        assert exit_code == 0

def teardown_module(module):
    print ("")
    print ("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class test_1_creation(unittest2.TestCase):

    def setUp(self):
        print ""

    def tearDown(self):
        print ""

    def test_creation(self):
        print "--- creation"

        be = BackendConnection(backend_address)
        assert be
        print "Backend object:", be

        be2 = BackendConnection(backend_address)
        assert be2
        print "Backend object:", be2

        # Objet is a singleton
        assert be == be2

class test_2_login(unittest2.TestCase):

    def setUp(self):
        print ""

    def tearDown(self):
        print ""

    def test_login(self):
        print "--- login"

        be = BackendConnection(backend_address)
        assert be
        print "Backend object:", be

        be.login('admin', 'fake')
        assert not be.connected

        be.login('admin', 'admin')
        assert be.connected


class test_3_get(unittest2.TestCase):

    def setUp(self):
        print "Login..."
        self.be = BackendConnection(backend_address)
        assert self.be
        self.be.login('admin', 'admin')
        assert self.be.connected

        print "Logged in"

    def tearDown(self):
        print ""

    def test_count(self):
        print "--- count"

        # Count all contacts
        result = self.be.count('contact')
        print "Result: %s", result
        self.assertEqual(result, 4)

        parameters = {'where': {"name":"admin"}}
        result = self.be.count('contact', parameters)
        print "Result: %s", result
        self.assertEqual(result, 1)

        parameters = {'where': {"name":"fake"}}
        result = self.be.count('contact', parameters)
        print "Result: %s", result
        self.assertEqual(result, 0) # Not found !

        # Get admin contact
        parameters = {'where': {"name":"admin"}}
        result = self.be.get('contact', parameters)
        print result
        self.assertEqual(len(result), 1)    # Only 1 is admin

        result = self.be.count('contact', result[0]['_id'])
        print "Result: %s", result
        self.assertEqual(result, 1)

    def test_get(self):
        print "--- get"

        # Get all contacts
        result = self.be.get('contact')
        print "%s contacts: " % len(result)
        for contact in result:
            self.assertIn('name', contact)
            self.assertIn('_total', contact)    # Each element has an extra _total attribute !
            print " - %s (one out of %d)" % (contact['name'], contact['_total'])
        self.assertEqual(len(result), 4)        # Default configuration has 4 contacts

        parameters = {'where': {"name":"fake"}}
        result = self.be.get('contact', parameters)
        print result
        self.assertEqual(len(result), 0)    # Not found

        parameters = {'where': {"name":"admin"}}
        result = self.be.get('contact', parameters)
        print result
        self.assertEqual(len(result), 1)    # Only 1 is admin
        admin_id = result[0]['_id']
        print "Administrator id:", admin_id

        result = self.be.get('contact', result[0]['_id'])
        print "Result: %s", result
        self.assertEqual(len(result), 1)    # Only 1 is admin
        self.assertEqual(result[0]['_id'], admin_id)

        # Directly address object in the backend
        result = self.be.get('contact/' + result[0]['_id'])
        print "--- Result: %s", result
        self.assertEqual(len(result), 40)    # 40 attributes in the result
        self.assertEqual(result['_id'], admin_id)

    def test_get_all(self):
        print "--- get all"

        # Get one page of services
        result = self.be.get('service')
        print "Backend pagination default:", BACKEND_PAGINATION_DEFAULT
        print "Backend pagination limit:", BACKEND_PAGINATION_LIMIT

        print "%s services: " % len(result)
        for service in result:
            print " - %s" % service['name']
        assert len(result) == BACKEND_PAGINATION_LIMIT
        # Should be DEFAULT and not LIMIT ... See https://github.com/Alignak-monitoring-contrib/alignak-backend/issues/52
        # assert len(result) == BACKEND_PAGINATION_DEFAULT # Default backend pagination

        # Get all services
        result = self.be.get('service', all_elements=True)
        print "%s services: " % len(result)
        for service in result:
            print " - %s" % service['name']
        assert len(result) == 89
