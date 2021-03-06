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

from __future__ import print_function

import time

import unittest2

from alignak_webui import set_app_config
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.settings import Settings

helper = Helper()


def setup_module():
    print ("")

    # Get configuration from only one file ...
    print ("read configuration")
    cfg = Settings("settings.cfg")
    found_cfg_files = cfg.read('Alignak-WebUI')
    assert found_cfg_files
    set_app_config(cfg)


class TestHelper(unittest2.TestCase):
    def setUp(self):
        print("")
        print("setting up ...")

    def tearDown(self):
        print("")
        print("tearing down ...")

    def test_01_print_date(self):
        print("---")

        now = time.time()

        # Timestamp errors
        s = helper.print_date(None)
        print("Result:", s)
        self.assert_(s == 'n/a')

        s = helper.print_date(0)
        print("Result:", s)
        self.assert_(s == 'n/a')

        # Now, default format
        s = helper.print_date(now)
        print("Result:", s)

        # Now, specified format
        s = helper.print_date(now, fmt='%Y-%m-%d')
        print("Result:", s)

        s = helper.print_date(now, fmt='%H:%M:%S')
        print("Result:", s)

        # Now, force local specified format
        s = helper.print_date(now, fmt=None)
        print("Result:", s)

    def test_02_print_duration(self):
        print("---")

        now = time.time()

        # Timestamp errors
        s = helper.print_duration(None)
        print("Result:", s)
        self.assert_(s == 'n/a')
        s = helper.print_duration(0)
        print("Result:", s)
        self.assert_(s == 'n/a')

        # Now, default format
        s = helper.print_duration(now)
        print("Result:", s)
        self.assert_(s == 'Just now')
        # 2s ago
        s = helper.print_duration(now - 2)
        print("Result:", s)
        self.assert_(s == 'Just now')

        # In the past ...
        # 4s ago
        s = helper.print_duration(now - 4)
        print("Result:", s)
        self.assertEqual(s, ' 4s ago')

        # Only the duration string
        s = helper.print_duration(now - 4, duration_only=True)
        print("Result:", s)
        self.assertEqual(s, '4s')

        # Got 2minutes
        s = helper.print_duration(now - 120)
        print("Result:", s)
        self.assertEqual(s, ' 2m ago')

        # Go 2hours ago
        s = helper.print_duration(now - 3600 * 2)
        print("Result:", s)
        self.assertEqual(s, ' 2h ago')

        # Go 2 days ago
        s = helper.print_duration(now - 3600 * 24 * 2)
        print("Result:", s)
        self.assertEqual(s, ' 2d ago')

        # Go 2 weeks ago
        s = helper.print_duration(now - 86400 * 14)
        print("Result:", s)
        self.assertEqual(s, ' 2w ago')

        # Go 2 months ago
        s = helper.print_duration(now - 86400 * 56)
        print("Result:", s)
        self.assertEqual(s, ' 2M ago')

        # Go 1 year ago
        s = helper.print_duration(now - 86400 * 365 * 2)
        print("Result:", s)
        self.assertEqual(s, ' 2y ago')

        # Now a mix of all of this :)
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56)
        print("Result:", s)
        self.assertEqual(s, ' 2M 2w 2d 2h 2m 2s ago')

        # Now with a limit, because here it's just a nightmare to read
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=2)
        print("Result:", s)
        self.assertEqual(s, ' 2M 2w ago')

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=3)
        print("Result:", s)
        self.assertEqual(s, ' 2M 2w 2d ago')

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=4)
        print("Result:", s)
        self.assertEqual(s, ' 2M 2w 2d 2h ago')

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=5)
        print("Result:", s)
        self.assertEqual(s, ' 2M 2w 2d 2h 2m ago')

        # Not a timestamp but a duration !
        s = helper.print_duration(2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56,
                                  x_elts=2, duration_only=True, ts_is_duration=True)
        print("Result:", s)
        self.assertEqual(s, '2M 2w')
        s = helper.print_duration(2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56,
                                  x_elts=6, duration_only=True, ts_is_duration=True)
        print("Result:", s)
        self.assertEqual(s, '2M 2w 2d 2h 2m 2s')

        # Return to the future
        # Get the 2s ago
        s = helper.print_duration(now + 2)
        print("Result:", s)
        self.assertEqual(s, 'Very soon')

        s = helper.print_duration(now + 4)
        print("Result:", s)
        self.assertEqual(s, 'in 4s')

        # Go 2 minutes
        s = helper.print_duration(now + 120)
        print("Result:", s)
        self.assertEqual(s, 'in 2m')

        # Go 2 hours ago
        s = helper.print_duration(now + 3600 * 2)
        print("Result:", s)
        self.assertEqual(s, 'in 2h')

        # Go 2 days ago
        s = helper.print_duration(now + 3600 * 24 * 2)
        print("Result:", s)
        self.assertEqual(s, 'in 2d')

        # Go 2 weeks ago
        s = helper.print_duration(now + 86400 * 14)
        print("Result:", s)
        self.assertEqual(s, 'in 2w')

        # Go 2 months ago
        s = helper.print_duration(now + 86400 * 56)
        print("Result:", s)
        self.assertEqual(s, 'in 2M')

        # Go 1 year ago
        s = helper.print_duration(now + 86400 * 365 * 2)
        print("Result:", s)
        self.assertEqual(s, 'in 2y')

        # Now a mix of all of this :)
        s = helper.print_duration(
            now + 2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56)
        print("Result:", s)
        self.assertEqual(s, 'in 2M 2w 2d 2h 2m 2s')

        # Now with a limit, because here it's just a nightmare to read
        s = helper.print_duration(
            now + 2 - 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56, x_elts=2)
        print("Result:", s)
        self.assertEqual(s, 'in 2M 2w')

    def test_03_print_on_off(self):
        print("---")

        # Call errors
        s = helper.get_on_off()
        print("Result:", s)
        self.assertEqual(s, '<i title="Disabled" class="fa fa-fw fa-close text-danger"></i>')

        # Status only
        s = helper.get_on_off(False)
        print("Result:", s)
        self.assertEqual(s, '<i title="Disabled" class="fa fa-fw fa-close text-danger"></i>')

        s = helper.get_on_off(True)
        print("Result:", s)
        self.assertEqual(s, '<i title="Enabled" class="fa fa-fw fa-check text-success"></i>')

        # Title
        s = helper.get_on_off(False, 'Title')
        print("Result:", s)
        self.assertEqual(s, '<i title="Title" class="fa fa-fw fa-close text-danger"></i>')

        s = helper.get_on_off(True, 'Title')
        print("Result:", s)
        self.assertEqual(s, '<i title="Title" class="fa fa-fw fa-check text-success"></i>')

        # Message
        s = helper.get_on_off(False, message='Message')
        print("Result:", s)
        self.assertEqual(s, '<i title="Disabled" class="fa fa-fw fa-close text-danger">Message</i>')

        s = helper.get_on_off(True, message='Message')
        print("Result:", s)
        self.assertEqual(s, '<i title="Enabled" class="fa fa-fw fa-check text-success">Message</i>')

        # Title and message
        s = helper.get_on_off(True, title='Title', message='Message')
        print("Result:", s)
        self.assertEqual(s, '<i title="Title" class="fa fa-fw fa-check text-success">Message</i>')

        # Title as array
        s = helper.get_on_off(True, title=['on', 'off'], message='Message')
        print("Result:", s)
        self.assertEqual(s, '<i title="on" class="fa fa-fw fa-check text-success">Message</i>')

        s = helper.get_on_off(False, title=['on', 'off'], message='Message')
        print("Result:", s)
        self.assertEqual(s, '<i title="off" class="fa fa-fw fa-close text-danger">Message</i>')

    def test_04_navigation_control(self):
        print("---")

        # Parameters: page, total, start, count, nb_max_items
        s = helper.get_pagination_control('test', 0, 0, 0, 0)
        self.assertEqual(s, [('test', 0, 0, 0, False)])
        s = helper.get_pagination_control('test', 0, 0)
        # Default is 25 elements per page
        self.assertEqual(s, [('test', 0, 25, 0, False)])

        # first page, default pagination: 25 elements/page, 5 pages/sequence
        s = helper.get_pagination_control('test', 1, 0)
        print("Result:", s)
        # At least a global element and a local element ...
        self.assertEqual(len(s), 2)
        # Still the same page
        s = helper.get_pagination_control('test', 25, 0)
        print("Result:", s)
        self.assertEqual(len(s), 2)
        s = helper.get_pagination_control('test', 26, 0)
        print("Result:", s)
        self.assertEqual(len(s), 3)
        s = helper.get_pagination_control('test', 51, 0)
        print("Result:", s)
        self.assertEqual(len(s), 4)
        s = helper.get_pagination_control('test', 76, 0)
        print("Result:", s)
        # More than 5 pages ... must have forward controls (2 more elements than expected).
        self.assertEqual(len(s), 7)
        s = helper.get_pagination_control('test', 101, 0)
        print("Result:", s)
        self.assertEqual(len(s), 8)

        # first page, default pagination: 5 elements/page, 5 pages/sequence
        s = helper.get_pagination_control('test', 1, 0, 5)
        print("Result:", s)
        self.assertEqual(len(s), 2)
        s = helper.get_pagination_control('test', 11, 0, 5)
        print("Result:", s)
        self.assertEqual(len(s), 4)
        # More than 5 pages ... must have forward controls.
        s = helper.get_pagination_control('test', 26, 0, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)

        # List pages, default pagination: 5 elements/page, 5 pages/sequence
        # More than 5 pages ... must have forward controls.
        s = helper.get_pagination_control('test', 40, 0, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)
        s = helper.get_pagination_control('test', 40, 5, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)
        s = helper.get_pagination_control('test', 40, 10, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)
        # Current page no more in the page sequence ... must have also backward controls.
        s = helper.get_pagination_control('test', 40, 15, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)
        s = helper.get_pagination_control('test', 40, 20, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)
        # Last page is now in the page sequence ... no more forward controls.
        s = helper.get_pagination_control('test', 40, 25, 5)
        print("Result:", s)
        self.assertEqual(len(s), 10)
        s = helper.get_pagination_control('test', 40, 30, 5)
        print("Result:", s)
        self.assertEqual(len(s), 10)
        s = helper.get_pagination_control('test', 40, 35, 5)
        print("Result:", s)
        self.assertEqual(len(s), 10)
        s = helper.get_pagination_control('test', 40, 40, 5)
        print("Result:", s)
        self.assertEqual(len(s), 8)

    def test_05_search(self):
        print("---")

        s = helper.decode_search("")
        print("Result:", s)
        assert s == {}

        s = helper.decode_search("status:active")
        print("Result:", s)
        assert s == {'status': 'active'}

        s = helper.decode_search("status:active name:name")
        print("Result:", s)
        assert s == {'status': 'active', 'name': 'name'}

        s = helper.decode_search("status:!active")
        print("Result:", s)
        assert s == {'$ne': {'status': 'active'}}

        s = helper.decode_search("state_id:1|2|3")
        print("Result:", s)
        assert s == {'$in': {'state_id': ['1', '2', '3']}}

    @unittest2.skip("Replaced by another test because of stars :)")
    def test_06_print_business_impact(self):
        print("---")

        # Invalid values
        s = helper.get_html_business_impact(-1, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == 'n/a - value')
        s = helper.get_html_business_impact(6, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'n/a - value')
        s = helper.get_html_business_impact(0, icon=False, text=False)
        print("Result:", s)
        self.assert_(s == 'n/a - parameters')

        # Default with stars
        s = helper.get_html_business_impact(0, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '')  # Nothing
        s = helper.get_html_business_impact(1, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '')  # Nothing
        s = helper.get_html_business_impact(2, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '')  # Nothing
        s = helper.get_html_business_impact(3, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '<i class="fa fa-star text-primary"></i>')  # 1 star
        s = helper.get_html_business_impact(4, icon=True, text=False)
        print("Result:", s)
        self.assert_(
            s == '<i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')  # 2 stars
        s = helper.get_html_business_impact(5, icon=True, text=False)
        print("Result:", s)
        self.assert_(
            s == '<i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')  # 3 stars

        # Default with text
        s = helper.get_html_business_impact(0, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'None')
        s = helper.get_html_business_impact(1, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Low')
        s = helper.get_html_business_impact(2, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Normal')
        s = helper.get_html_business_impact(3, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Important')
        s = helper.get_html_business_impact(4, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Very important')
        s = helper.get_html_business_impact(5, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Business critical')

        # Default with icon and text
        s = helper.get_html_business_impact(0, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'None')
        s = helper.get_html_business_impact(1, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Low')
        s = helper.get_html_business_impact(2, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Normal')
        s = helper.get_html_business_impact(3, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Important <i class="fa fa-star text-primary"></i>')
        s = helper.get_html_business_impact(4, icon=True, text=True)
        print("Result:", s)
        self.assert_(
            s == 'Very important <i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')
        s = helper.get_html_business_impact(5, icon=True, text=True)
        print("Result:", s)
        self.assert_(
            s == 'Business critical <i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')

    def test_06_bis_print_business_impact(self):
        print("---")

        # Invalid values
        s = helper.get_html_business_impact(-1, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == 'n/a - value')
        s = helper.get_html_business_impact(6, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'n/a - value')
        s = helper.get_html_business_impact(0, icon=False, text=False)
        print("Result:", s)
        self.assert_(s == 'n/a - parameters')

        # Default with stars
        s = helper.get_html_business_impact(0, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '')  # Nothing
        s = helper.get_html_business_impact(1, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '<i class="fa fa-star text-primary"></i>')  # 1 star
        s = helper.get_html_business_impact(2, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '<i class="fa fa-star text-primary"></i>' * 2)  # 2 stars
        s = helper.get_html_business_impact(3, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '<i class="fa fa-star text-primary"></i>' * 3)  # 3 stars
        s = helper.get_html_business_impact(4, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '<i class="fa fa-star text-primary"></i>' * 4)  # 3 stars
        s = helper.get_html_business_impact(5, icon=True, text=False)
        print("Result:", s)
        self.assert_(s == '<i class="fa fa-star text-primary"></i>' * 5)  # 3 stars

        # Default with text
        s = helper.get_html_business_impact(0, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'None')
        s = helper.get_html_business_impact(1, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Low')
        s = helper.get_html_business_impact(2, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Normal')
        s = helper.get_html_business_impact(3, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Important')
        s = helper.get_html_business_impact(4, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Very important')
        s = helper.get_html_business_impact(5, icon=False, text=True)
        print("Result:", s)
        self.assert_(s == 'Business critical')

        # Default with icon and text
        s = helper.get_html_business_impact(0, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'None')
        s = helper.get_html_business_impact(1, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Low ' + '<i class="fa fa-star text-primary"></i>' * 1)
        s = helper.get_html_business_impact(2, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Normal ' + '<i class="fa fa-star text-primary"></i>' * 2)
        s = helper.get_html_business_impact(3, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Important ' + '<i class="fa fa-star text-primary"></i>' * 3)
        s = helper.get_html_business_impact(4, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Very important ' + '<i class="fa fa-star text-primary"></i>' * 4)
        s = helper.get_html_business_impact(5, icon=True, text=True)
        print("Result:", s)
        self.assert_(s == 'Business critical ' + '<i class="fa fa-star text-primary"></i>' * 5)

    def test_07_bis_print_timeperiod(self):
        print("---")

        # Invalid values
        s = helper.get_html_timeperiod(None)
        print("Result:", s)
        self.assertEqual(s, '')

        tp = TimePeriod(
            {'_updated': 1465548247, '_total': 5, '_type': 'timeperiod', 'definition_order': 100,
             '_default_date': 0, '_comment': '', 'is_active': True,
             '_name': u'All time default 24x7',
             'dateranges': [{u'monday': u'00:00-24:00'}, {u'tuesday': u'00:00-24:00'},
                            {u'wednesday': u'00:00-24:00'}, {u'thursday': u'00:00-24:00'},
                            {u'friday': u'00:00-24:00'}, {u'saturday': u'00:00-24:00'},
                            {u'sunday': u'00:00-24:00'}], '_alias': u'', '_links': {
                u'self': {u'href': u'timeperiod/575a7dd74c988c170e857988',
                          u'title': u'Timeperiod'}}, '_realm': u'575a7dd74c988c170e857987',
             '_created': 1465548247, 'exclude': [], '_status': 'unknown',
             '_id': u'575a7dd74c988c170e857988',
             '_etag': u'e9f5fb031b79f9abdc42f44d413f8220c321767b', 'imported_from': u''})
        s = helper.get_html_timeperiod(tp)
        print("Result:", s)
        self.assertEqual(s,
                         '<button class="btn btn-default btn-xs btn-block" type="button"data-toggle="collapse" data-target="#html_tp_575a7dd74c988c170e857988" aria-expanded="false" aria-controls="html_tp_575a7dd74c988c170e857988">All time default 24x7</button><div class="collapse" id="html_tp_575a7dd74c988c170e857988"><div class="well"><ul class="list-group"><li class="list-group-item"><span class="fa fa-check">&nbsp;monday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-check">&nbsp;tuesday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-check">&nbsp;wednesday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-check">&nbsp;thursday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-check">&nbsp;friday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-check">&nbsp;saturday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-check">&nbsp;sunday - 00:00-24:00</li></ul></div></div>')
