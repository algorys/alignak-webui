#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016:
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

"""
    Plugin Worldmap
"""

from logging import getLogger

from bottle import request

from alignak_webui import _
from alignak_webui.plugins.common.common import get_widget
from alignak_webui.utils.helper import Helper

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Plugin's parameters
plugin_parameters = {
    'default_zoom': 6,
    'default_lng': 1.87528,
    'default_lat': 46.60611,
    'hosts_level': [1, 2, 3, 4, 5],
    'services_level': [1, 2, 3, 4, 5],
    'layer': ''
}


def get_worldmap():
    """
    Get the hosts list to build a worldmap
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Pagination and search
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = Helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // (count + 1),
        'max_results': count,
        'sort': '-_id',
        'where': where
    }

    # Get valid hosts
    valid_hosts = get_valid_elements(search)

    # Get last total elements count
    total = len(valid_hosts)
    count = min(len(valid_hosts), total)

    return {
        'mapId': 'hostsMap',
        'params': plugin_parameters,
        'hosts': valid_hosts,
        'pagination': webui.helper.get_pagination_control('/worldmap', total, start, count),
        'title': request.query.get('title', _('Hosts worldmap'))
    }


def get_valid_elements(search):
    """
    Get hosts valid for a map:
    - must have custom variables with GPS coordinates
    - must have a business_impact that match the one defined in this plugin parameters
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Get elements from the data manager
    hosts = datamgr.get_hosts(search)
    logger.info("worldmap, search valid hosts")

    valid_hosts = []
    for host in hosts:
        logger.debug("worldmap, found host '%s'", host.name)

        if host.business_impact not in plugin_parameters['hosts_level']:
            continue

        if host.position:
            logger.info("worldmap, host '%s' located: %s", host.name, host.position)
            valid_hosts.append(host)

    return valid_hosts


def get_worldmap_widget(embedded=False, identifier=None, credentials=None):
    """
    Get the worldmap widget
    """
    return get_widget(get_valid_elements, 'host', embedded, identifier, credentials)


# We export our properties to the webui
pages = {
    get_worldmap: {
        'name': 'Worldmap',
        'route': '/worldmap',
        'view': 'worldmap'
    },

    get_worldmap_widget: {
        'name': 'Worlmap widget',
        'route': '/worldmap/widget',
        'method': 'POST',
        'view': 'worldmap_widget',
        'widgets': [
            {
                'id': 'worldmap_table',
                'for': ['external', 'dashboard'],
                'name': _('Worldmap widget'),
                'template': 'worldmap_widget',
                'icon': 'globe',
                'description': _(
                    '<h4>Worldmap widget</h4>Displays a world map of the monitored system '
                    'hosts.<br>The number of hosts on the map can be defined in the widget '
                    'options. The list of hosts can be filtered thanks to regex on the '
                    'host name.'
                ),
                'picture': 'htdocs/img/worldmap_widget.png',
                'options': {
                    'search': {
                        'value': '',
                        'type': 'text',
                        'label': _('Filter (ex. status:ok)')
                    },
                    'count': {
                        'value': -1,
                        'type': 'int',
                        'label': _('Number of elements')
                    },
                    'filter': {
                        'value': '',
                        'type': 'hst_srv',
                        'label': _('Host/service name search')
                    }
                }
            }
        ]
    }
}
