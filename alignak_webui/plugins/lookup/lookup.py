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
    Plugin Lookup
"""

import json
from logging import getLogger

from bottle import request

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None


def lookup():
    """
    Search in the livestate for an element name
    """
    datamgr = request.environ['beaker.session']['datamanager']

    query = request.query.get('query', '')

    logger.warning("lookup: %s", query)

    elements = datamgr.get_livestate(search={'where': {'name': {"$regex": ".*" + query + ".*"}}})
    names = [e.name for e in elements]
    logger.warning("lookup: %s", names)

    return json.dumps(names)


pages = {
    lookup: {
        'name': 'GetLookup',
        'route': '/lookup',
        'method': 'GET'
    }
}
