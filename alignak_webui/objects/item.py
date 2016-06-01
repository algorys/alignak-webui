#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, fixme,too-many-arguments, too-many-public-methods
# pylint: disable=too-many-nested-blocks, too-many-locals, too-many-return-statements
# pylint: disable=attribute-defined-outside-init, protected-access

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
    This module contains the classes used to manage the application objects with the data manager.
"""

import time
from datetime import datetime, timedelta

import locale

import traceback
from logging import getLogger, INFO

from calendar import timegm
from dateutil import tz

from alignak_webui import get_app_config, _

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
logger.setLevel(INFO)


class ItemState(object):
    '''
    Singleton design pattern ...
    '''
    class __ItemState(object):
        '''
        Base class for all objects state management (displayed icon, ...)
        '''

        def __init__(self):
            '''
            Create
            '''
            self.states = None

            # Get global configuration
            app_config = get_app_config()
            if not app_config:  # pragma: no cover, should not happen
                return

            self.object_types_states = {}
            self.default_states = {}
            for s in app_config:
                s = s.split('.')
                if s[0] not in ['items']:
                    continue

                logger.debug("ItemState, item configuration element: %s", s)
                if s[1] == 'item':
                    if s[2] not in self.default_states:
                        self.default_states[s[2]] = []
                    continue

                if s[1] not in ['content', 'back', 'front', 'badge']:
                    if s[1] not in self.object_types_states:
                        self.object_types_states[s[1]] = []

                    if s[2] and s[2] not in self.object_types_states[s[1]]:
                        self.object_types_states[s[1]].append(s[2])

            logger.debug("ItemState, object types and states: %s", self.object_types_states)
            # print "Objects types: ", self.object_types_states
            logger.debug("ItemState, default states: %s", self.default_states)

            # Application locales, timezone, ...
            # Set timezones
            self.tz_from = tz.gettz('UTC')
            logger.debug(
                "Set default time zone: %s",
                app_config.get("timezone", 'Europe/Paris')
            )
            self.tz_to = tz.gettz(app_config.get("timezone", 'Europe/Paris'))

            # Set class date format
            logger.debug(
                "Set default time format string: %s",
                app_config.get("timeformat", '%Y-%m-%d %H:%M:%S')
            )
            self.date_format = app_config.get("timeformat", '%Y-%m-%d %H:%M:%S')

            # For each defined object type and object type state ...
            self.states = {}
            for object_type in self.object_types_states:
                self.states[object_type] = {}
                for state in self.object_types_states[object_type]:
                    self.states[object_type][state] = {}
                    for prop in ['text', 'icon', 'class']:
                        search = "items.%s.%s.%s" % (object_type, state, prop)
                        if "items.%s.%s.%s" % (object_type, state, prop) in app_config:
                            self.states[object_type][state][prop] = app_config.get(search)
                        else:  # pragma: no cover, should not happen
                            self.states[object_type][state][prop] = \
                                app_config.get("items.%s.%s" % (state, prop), '')

                # If no states is defined for element type, define default states ...
                # if not self.states:
                for state in self.default_states:
                    if state not in self.states[object_type]:
                        self.states[object_type][state] = {}
                        for prop in ['text', 'icon', 'class']:
                            self.states[object_type][state][prop] = \
                                app_config.get("items.item.%s.%s" % (state, prop), '')

                # Build a self state view with content, back and front templates
                self.states[object_type]['state_view'] = {}
                for prop in ['content', 'back', 'front', 'badge']:
                    search = "items.%s.%s" % (object_type, prop)
                    if "items.%s.%s" % (object_type, prop) in app_config:  # pragma: no cover
                        self.states[object_type]['state_view'][prop] = \
                            app_config.get(search)
                    else:
                        self.states[object_type]['state_view'][prop] = \
                            app_config.get("items.%s" % (prop))

                logger.debug(
                    " --- class configuration: %s: %s",
                    object_type, self.states[object_type]
                )

        def get_objects_types(self):
            '''
                Return all the configured objects types

                All other object type will use the default 'item' configuration
            '''
            return [s for s in self.states]

        def get_icon_states(self, object_type=None):
            ''' Return all the configured states for an object type '''
            if not object_type:
                return self.states
            if object_type in self.states:
                return self.states[object_type]
            return []

        def get_default_states(self):
            ''' Return all the configured states for a generic item '''
            return [s for s in self.default_states]

        def get_icon_state(self, object_type, status):
            ''' Return the configured state for an object type '''
            if not object_type or not status:
                return None

            if status not in self.get_icon_states(object_type):
                return None

            for s in self.get_icon_states(object_type):
                if status == s:
                    return self.get_icon_states(object_type)[s]

        def get_html_state(self, object_type, object_item, extra='', icon=True, text=False,
                           label='', disabled=False):
            """
            Returns an item status as HTML text and icon if needed

            If parameters are not valid, returns 'n/a'

            If disabled is True, the class does not depend upon object status and is always
            font-greyed

            If a label is specified, text must be True, and the label will be used instead
            of the built text.

            If object status contains '.' characters they are replaced with '_'

            Text and icon are defined in the application configuration file.

            :param object_type: element type
            :type object_type: string
            :param object_item: element
            :type object: Item class based object

            :param extra: extra string replacing ##extra##, and set opacity to 0.5
            :type extra: string

            :param text: include text in the response
            :type text: boolean
            :param icon: include icon in the response
            :type icon: boolean
            :return: formatted status HTML string
            :rtype: string
            """
            if not object_type:  # pragma: no cover, should not happen
                return 'n/a - element'

            if not object_item:  # pragma: no cover, should not happen
                return 'n/a - object'

            if not icon and not text:
                return 'n/a - icon/text'

            status = object_item.get_status()
            status = status.replace('.', '_').lower()
            if object_type in self.get_objects_types():
                if status not in self.get_icon_states(object_type):
                    return 'n/a - status: ' + status
            else:
                if status not in self.get_default_states():  # pragma: no cover, should not happen
                    return 'n/a - default status: ' + status

            cfg_state = self.get_icon_state(object_type, status)
            if object_type not in self.get_objects_types() and status in self.get_default_states():
                cfg_state = self.get_icon_state("user", status)
            logger.debug("get_html_state, states: %s", cfg_state)

            cfg_state_view = self.get_icon_state(object_type, 'state_view')
            if object_type not in self.get_objects_types():
                cfg_state_view = self.get_icon_state("user", 'state_view')
            if not cfg_state_view:  # pragma: no cover, should not happen
                return 'n/a - cfg_state_view'
            logger.debug("get_html_state, states view: %s", cfg_state_view)

            # Text
            res_icon_state = cfg_state['icon']
            res_icon_text = cfg_state['text']
            res_icon_class = 'item_' + cfg_state['class']
            res_text = res_icon_text

            if text and not icon:
                return res_text

            # Icon
            res_icon_global = cfg_state_view['content']
            res_icon_back = cfg_state_view['back']
            res_icon_front = cfg_state_view['front']

            res_extra = "fa-inverse"
            if extra:
                res_extra = extra
            res_opacity = ""
            if extra:
                res_opacity = 'style="opacity: 0.5"'

            # Assembling ...
            item_id = object_item.get_id()
            res_icon = res_icon_global
            res_icon = res_icon.replace("##type##", object_type)
            res_icon = res_icon.replace("##id##", item_id)
            res_icon = res_icon.replace("##name##", object_item.get_name())
            res_icon = res_icon.replace("##state##", object_item.get_state())
            res_icon = res_icon.replace("##back##", res_icon_back)
            res_icon = res_icon.replace("##front##", res_icon_front)
            res_icon = res_icon.replace("##status##", status.lower())
            if not disabled:
                res_icon = res_icon.replace("##class##", res_icon_class)
            else:
                res_icon = res_icon.replace("##class##", "font-greyed")

            res_icon = res_icon.replace("##icon##", res_icon_state)
            res_icon = res_icon.replace("##extra##", res_extra)
            res_icon = res_icon.replace("##title##", res_text)
            res_icon = res_icon.replace("##opacity##", res_opacity)
            if label:
                res_icon = res_icon.replace("##text##", label)
            elif text:
                res_icon = res_icon.replace("##text##", res_text)
            else:
                res_icon = res_icon.replace("##text##", "")

            logger.debug("get_html_state, res_icon: %s", res_icon)
            return res_icon

        def get_html_badge(self, object_type, object_item, label='', disabled=False):
            """
            Returns an item status as HTML text and icon if needed

            If parameters are not valid, returns 'n/a'

            If disabled is True, the class does not depend upon status and is always font-greyed

            If a label is specified, text must be True, and the label will be used instead
            of the built text.

            Text and icon are defined in the application configuration file.

            :param element: force element type (to get generic element type view)
            :type element: string
            :param object_item: element
            :type object: Item class based object

            :param text: include text in the response
            :type text: boolean
            :param icon: include icon in the response
            :type icon: boolean
            :return: formatted status HTML string
            :rtype: string
            """
            if not object_type:  # pragma: no cover, should not happen
                return 'n/a - element'

            if not object_item:  # pragma: no cover, should not happen
                return 'n/a - object'

            status = object_item.get_status()
            status = status.replace('.', '_').lower()
            if object_type in self.get_objects_types():
                if status not in self.get_icon_states(object_type):
                    return 'n/a - status: ' + status
            else:  # pragma: no cover, not tested
                if status not in self.get_default_states():
                    return 'n/a - default status: ' + status

            cfg_state = self.get_icon_state(object_type, status)
            if object_type not in self.get_objects_types() and status in self.get_default_states():
                cfg_state = self.get_icon_state("user", status)
            logger.debug("get_html_badge, states: %s", cfg_state)

            cfg_state_view = self.get_icon_state(object_type, 'state_view')
            if object_type not in self.get_objects_types():
                cfg_state_view = self.get_icon_state("user", 'state_view')
            if not cfg_state_view:  # pragma: no cover, should not happen
                return 'n/a - cfg_state_view'
            logger.debug("get_html_badge, states view: %s", cfg_state_view)

            # Text
            res_icon_state = cfg_state['icon']
            res_icon_text = cfg_state['text']
            res_icon_class = 'item_' + cfg_state['class']
            res_text = res_icon_text

            # Icon
            res_icon_badge = cfg_state_view['badge']
            if not res_icon_badge:  # pragma: no cover, should not happen
                return 'n/a - res_icon_badge'

            res_extra = "fa-inverse"
            res_opacity = ""

            # Assembling ...
            item_id = object_item.get_id()
            res_icon = res_icon_badge
            res_icon = res_icon.replace("##type##", object_type)
            res_icon = res_icon.replace("##id##", item_id)
            res_icon = res_icon.replace("##name##", object_item.get_name())
            res_icon = res_icon.replace("##state##", object_item.get_state())
            res_icon = res_icon.replace("##status##", status.lower())
            if not disabled:
                res_icon = res_icon.replace("##class##", res_icon_class)
            else:
                res_icon = res_icon.replace("##class##", "font-greyed")

            res_icon = res_icon.replace("##icon##", res_icon_state)
            res_icon = res_icon.replace("##extra##", res_extra)
            res_icon = res_icon.replace("##title##", res_text)
            res_icon = res_icon.replace("##opacity##", res_opacity)
            if label:
                res_icon = res_icon.replace("##text##", label)
            else:
                res_icon = res_icon.replace("##text##", "")

            logger.debug("get_html_badge, res_icon: %s", res_icon)
            return res_icon

    instance = None

    def __new__(cls):
        if not ItemState.instance:
            ItemState.instance = ItemState.__ItemState()
        return ItemState.instance

    def get_html_state(self, extra='', icon=True, text=False,
                       label='', disabled=False,
                       object_type='', object_item=None):  # pragma: no cover
        return self.instance.get_html_state(object_type, object_item,
                                            extra, icon, text, label, disabled)

    def get_html_badge(self,
                       label='', disabled=False,
                       object_type='', object_item=None):  # pragma: no cover
        return self.instance.get_html_badge(object_type, object_item,
                                            label, disabled)


class Item(object):
    '''
    Base class for all objects
    '''
    _count = 0
    _total_count = -1

    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'item'
    # _cache is a list of created objects
    _cache = {}

    # Default date used for bad formatted string dates
    _default_date = 0

    # Items states
    items_states = [
        # Ok
        "ok",
        # Warning
        "warning",
        # Critical
        "critical",
        # Unknown
        "unknown",
        # Not executed
        "not_executed"
    ]

    """ Manage cached objects """
    @classmethod
    def getType(cls):
        return cls._type

    @classmethod
    def getCount(cls):
        return cls._count

    @classmethod
    def getTotalCount(cls):
        return cls._total_count

    @classmethod
    def getCache(cls):
        return cls._cache

    @classmethod
    def cleanCache(cls):
        cls._next_id = 1
        cls._count = 0
        cls._cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new object

        If the provided arguments have a params dictionary that include an _id field,
        this field will be used as an unique object identifier. else, an auto generated
        _id field will be used to identify uniquely an object. If no parameters are provided
        a dummy _id==0 object will be created and used for each non parameters call.

        As of it, each new declaration without any parameter do not always create a new object!

        To reuse the dummy _id=0 object, specify '_id': '0' in the parameters.

        A newly created object is included in the global class _cache list that maintain a
        unique objects list for each class. If the new object identifier still exists in the
        unique objects list, no new object is created and the existing object is returned.

        Note: the _id attribute is always a string. If not, it is forced to be ...

        This function raises a ValueError exception if the first parameter is not a dictionary.
        '''
        id_property = getattr(cls, 'id_property', '_id')
        # print "Class %s, id_property: %s, params: %s" % (cls, id_property, params)

        _id = '0'
        if params:
            if not isinstance(params, dict):
                raise ValueError('Item.__new__: object parameters must be a dictionary!')

            if id_property in params:
                if not isinstance(params[id_property], basestring):
                    params[id_property] = str(params[id_property])
                _id = params[id_property]
            else:
                # TODO: change this ... always create type_0 object!
                _id = '%s_%d' % (cls.getType(), cls._next_id)
                params[id_property] = _id
                cls._next_id += 1

        if _id == '0':
            if not params:
                params = {}
            # Force _id in the parameters
            params.update({id_property: '%s_0' % (cls.getType())})

        if _id not in cls._cache:
            # print "Create a new %s (%s)" % (cls.getType(), _id)
            cls._cache[_id] = super(Item, cls).__new__(cls, params, date_format)
            cls._cache[_id]._type = cls.getType()
            cls._cache[_id]._default_date = cls._default_date

            # Call the new object create function
            cls._cache[_id]._create(params, date_format)
            cls._count += 1
        else:
            if params != cls._cache[_id].__dict__:
                # print "Update existing instance for: ", _id, params
                cls._cache[_id]._update(params, date_format)

        # print "Return existing instance for: ", _id, params
        return cls._cache[_id]

    def __del__(self):
        '''
        Delete an object (called only when no more reference exists for an object)
        '''
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)
        # print "Delete a %s (%s)" % (self.getType(), self._id)

    def _delete(self):
        '''
        Delete an object

        If the object exists in the cache, its reference is removed from the internal cache.
        '''
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)
        cls = self.__class__
        if self._id in cls._cache:
            logger.debug("Removing from cache...")
            del cls._cache[self._id]
            cls._count -= 1
            logger.debug(
                "Removed. Remaining in cache: %d / %d",
                cls.getCount(), len(cls.getCache())
            )

    def _create(self, params, date_format):
        '''
        Create an object (called only once when an object is newly created)

        Some specificities:
        1/ dates
            Parameters which name ends with date are considered as dates.
            _created and _updated parameters also.

            Accept dates as:
             - float (time.now()) as timestamp
             - formatted string as '%a, %d %b %Y %H:%M:%S %Z' (Tue, 01 Mar 2016 14:15:38 GMT)
             - else use date_format parameter to specify date string format

            If date can not be converted, parameter is set to a default date defined in the class

        2/ dicts
            If the object has declared some 'linked_XXX' prefixed attributes and the paramaters
            contain an 'XXX' field, this function creates a new object in the 'linked_XXX'
            attribute. The initial 'linked_XXX' attribute must contain the new object type!

            If the attribute is a simple dictionary, the new attribute contains the dictionary.

            This feature allows to create links between embedded objects of the backend.
        '''
        id_property = getattr(self.__class__, 'id_property', '_id')

        if id_property not in params:  # pragma: no cover, should never happen
            raise ValueError('No %s attribute in the provided parameters' % id_property)
        logger.debug(
            " --- creating a %s (%s - %s)",
            self.getType(), params[id_property], params['name'] if 'name' in params else ''
        )

        for key in params:
            logger.debug(" parameter: %s (%s) = %s", key, params[key].__class__, params[key])
            # Object must have declared a linked_ attribute ...
            if isinstance(params[key], dict) and hasattr(self, 'linked_' + key):
                # Linked resource type
                object_type = getattr(self, 'linked_' + key, None)
                logger.debug(" parameter: %s is a linked object: %s", key, object_type)
                if object_type is None:  # pragma: no cover, should never happen
                    setattr(self, key, params[key])
                    continue

                for k in globals().keys():
                    if isinstance(globals()[k], type) and \
                       '_type' in globals()[k].__dict__ and \
                       globals()[k]._type == object_type:
                        linked_object = globals()[k](params[key])
                        setattr(self, 'linked_' + key, linked_object)
                        setattr(self, key, linked_object['_id'])
                        logger.debug("Linked with %s (%s)", key, linked_object['_id'])
                        break
                continue

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in ['_created', '_updated']:
                if params[key]:
                    if isinstance(params[key], (int, long, float)):
                        # Date is received as a float or integer, store as a timestamp ...
                        # ... and assume it is UTC
                        # ----------------------------------------------------------------
                        setattr(self, key, params[key])
                    elif isinstance(params[key], basestring):
                        try:
                            # Date is supposed to be received as string formatted date
                            timestamp = timegm(time.strptime(params[key], date_format))
                            setattr(self, key, timestamp)
                        except ValueError:
                            logger.warning(
                                " parameter: %s = '%s' is not a valid string format: '%s'",
                                key, params[key], date_format
                            )
                            setattr(self, key, self.__class__._default_date)
                    else:
                        try:
                            # Date is supposed to be received as a struct time ...
                            # ... and assume it is local time!
                            # ----------------------------------------------------
                            timestamp = timegm(params[key].timetuple())
                            setattr(self, key, timestamp)
                        except TypeError:  # pragma: no cover, simple protection
                            logger.warning(
                                " parameter: %s is not a valid time tuple: '%s'",
                                key, params[key]
                            )
                            setattr(self, key, self.__class__._default_date)
                else:
                    setattr(self, key, self.__class__._default_date)
                continue

            try:
                setattr(self, key, params[key])
            except TypeError:  # pragma: no cover, should not happen
                logger.warning(" parameter TypeError: %s = %s", key, params[key])

        # Object name
        if not hasattr(self, 'name'):
            setattr(self, 'name', 'anonymous')

        # Object state
        if not hasattr(self, 'status'):
            setattr(self, 'status', 'unknown')

        logger.debug(" --- created %s (%s): %s", self.__class__, self[id_property], self.__dict__)

    def _update(self, params, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- updating a %s (%s)", self.__class__, self[id_property])

        if not isinstance(params, dict):
            params = params.__dict__
        for key in params:
            logger.debug(" --- parameter %s = %s", key, params[key])
            if isinstance(params[key], dict) and hasattr(self, 'linked_' + key):
                if not isinstance(getattr(self, 'linked_' + key, None), basestring):
                    # Does not contain a string, so update object ...
                    logger.debug(" Update object: %s = %s", key, params[key])
                    getattr(self, 'linked_' + key)._update(params[key])
                else:
                    # Else, create new linked object
                    object_type = getattr(self, 'linked_' + key, None)
                    if object_type is None:  # pragma: no cover, should never happen
                        setattr(self, key, params[key])
                        continue

                    for k in globals().keys():
                        if isinstance(globals()[k], type) and \
                           '_type' in globals()[k].__dict__ and \
                           globals()[k]._type == object_type:
                            linked_object = globals()[k](params[key])
                            setattr(self, 'linked_' + key, linked_object)
                            setattr(self, key, linked_object['_id'])
                            logger.debug(
                                "Linked: %s (%s) with %s (%s)",
                                self._type, self[id_property], key, linked_object.get_id()
                            )
                            break
                    continue
                continue

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in ['_created', '_updated']:
                if params[key]:
                    if isinstance(params[key], (int, long, float)):
                        # Date is received as a float or integer, store as a timestamp ...
                        # ... and assume it is UTC
                        # ----------------------------------------------------------------
                        setattr(self, key, params[key])
                    elif isinstance(params[key], basestring):
                        try:
                            # Date is supposed to be received as string formatted date
                            timestamp = timegm(time.strptime(params[key], date_format))
                            setattr(self, key, timestamp)
                        except ValueError:
                            logger.warning(
                                " parameter: %s = '%s' is not a valid string format: '%s'",
                                key, params[key], date_format
                            )
                            setattr(self, key, self.__class__._default_date)
                    else:
                        try:
                            # Date is supposed to be received as a struct time ...
                            # ... and assume it is local time!
                            # ----------------------------------------------------
                            timestamp = timegm(params[key].timetuple())
                            setattr(self, key, timestamp)
                        except TypeError:  # pragma: no cover, simple protection
                            logger.warning(
                                " parameter: %s is not a valid time tuple: '%s'",
                                key, params[key]
                            )
                            setattr(self, key, self.__class__._default_date)
                else:
                    setattr(self, key, self.__class__._default_date)
                continue

            try:
                setattr(self, key, params[key])
            except TypeError:  # pragma: no cover, should not happen
                logger.warning(" parameter TypeError: %s = %s", key, params[key])

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Initialize an object

        Beware: always called, even if the object is not newly created! Use _create function for
        initializing newly created objects.
        '''
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- initializing a %s (%s)", self._type, self[id_property])
        logger.debug(" --- initializing with %s and %s", params, date_format)

    def __repr__(self):
        return ("<%s, id: %s, name: %s, status: %s>") % (
            self.__class__._type, self.get_id(), self.get_name(), self.get_status()
        )

    def __getitem__(self, key):
        return getattr(self, key, None)

    def get_id(self):
        if hasattr(self.__class__, 'id_property'):
            return getattr(self, self.__class__.id_property, None)
        return getattr(self, '_id', None)

    def get_name(self):
        if hasattr(self.__class__, 'name_property'):
            return getattr(self, self.__class__.name_property, None)
        return getattr(self, 'name', None)

    def get_description(self):
        if hasattr(self.__class__, 'description_property'):
            return getattr(self, self.__class__.description_property, None)
        if hasattr(self, 'description'):
            return self.description
        return self.get_name()

    def get_status(self):
        if hasattr(self.__class__, 'status_property'):
            return getattr(self, self.__class__.status_property, None)
        return getattr(self, 'status', 'unknown')

    def get_state(self):
        state = getattr(self, 'state', 99)
        if isinstance(state, int):
            try:
                return self.__class__.items_states[state]
            except IndexError:
                return ''
        return state

    def get_icon_states(self):
        """
        Uses the ItemState singleton to get configured states for an item
        """
        item_state = ItemState()
        return item_state.get_icon_states()

    def get_html_state(self, extra='', icon=True, text=False,
                       label='', disabled=False, object_type=None, object_item=None):
        """
        Uses the ItemState singleton to display HTML state for an item
        """
        if not object_type:
            object_type = self.__class__._type

        if not object_item:
            object_item = self

        return ItemState().get_html_state(object_type, object_item,
                                          extra, icon, text, label, disabled)

    def get_html_badge(self, label='', disabled=False, object_type='', object_item=None):
        """
        Uses the ItemState singleton to display HTML badge for an item
        """
        if not object_type:
            object_type = self.__class__._type

        if not object_item:
            object_item = self

        return ItemState().get_html_badge(object_type, object_item,
                                          label, disabled)

    def get_date(self, _date=None, fmt=None):
        if _date == self.__class__._default_date:
            return _('Never dated!')

        item_state = ItemState()
        if not fmt and item_state.date_format:
            fmt = item_state.date_format

        # Make timestamp to datetime
        _date = datetime.utcfromtimestamp(_date)
        # Tell the datetime object that it's in UTC time zone since
        # datetime objects are 'naive' by default
        _date = _date.replace(tzinfo=item_state.tz_from)
        # Convert to required time zone
        _date = _date.astimezone(item_state.tz_to)
        if fmt:
            return _date.strftime(fmt)

        return _date.isoformat(' ')


class Contact(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'contact'
    # _cache is a list of created objects
    _cache = {}

    roles = {
        "user": _("User"),
        "power": _("Power user"),
        "administrator": _("Administrator")
    }

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new contact
        '''
        return super(Contact, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a contact (called only once when an object is newly created)
        '''
        if params and 'can_submit_commands' in params:
            params['read_only'] = False
            params.pop('can_submit_commands', None)

        super(Contact, self)._create(params, date_format)

        self.authenticated = False

        if not hasattr(self, 'email'):
            self.email = None

        if not hasattr(self, 'lync'):
            self.lync = None

        # Has a session token ?
        if not hasattr(self, 'token'):
            self.token = None

        # Is an administrator ?
        if not hasattr(self, 'is_admin'):
            self.is_admin = False

        # Can submit commands
        if not hasattr(self, 'read_only'):
            self.read_only = True

        # Can change dashboard
        if not hasattr(self, 'widgets_allowed'):
            self.widgets_allowed = False

        # Has a role ?
        if not hasattr(self, 'role'):
            self.role = self.get_role()

        if not hasattr(self, 'picture'):
            self.picture = '/static/photos/user_default'
            if self.name == 'anonymous':
                self.picture = '/static/photos/user_guest'
            else:
                if self.is_admin:
                    self.picture = '/static/photos/user_admin'

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a contact (called every time an object is updated)
        '''
        if params and 'can_submit_commands' in params:
            params['read_only'] = False
            params.pop('can_submit_commands', None)

        super(Contact, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a contact (called every time an object is invoked)
        '''
        super(Contact, self).__init__(params)

    def __repr__(self):
        if self.authenticated:
            return ("<Authenticated %s, id: %s, name: %s, role: %s>") % (
                self.__class__._type, self.get_id(), self.get_name(), self.get_role()
            )
        return ("<%s, id: %s, name: %s, role: %s>") % (
            self.__class__._type, self.get_id(), self.get_name(), self.get_role()
        )

    def get_friendly_name(self):
        return getattr(self, 'friendly_name', self.get_name())

    def get_token(self):
        return self.token

    def get_picture(self):
        return self.picture

    def get_username(self):
        if getattr(self, 'username', None):
            return self.username
        if getattr(self, 'contact_name', None):
            return self.contact_name
        return self.name

    def get_name(self):
        name = self.get_username()
        if getattr(self, 'friendly_name', None):
            return self.friendly_name
        elif getattr(self, 'realname', None):
            return "%s %s" % (getattr(self, 'firstname'), getattr(self, 'realname'))
        elif getattr(self, 'alias', None) and getattr(self, 'alias', None) != 'none':
            return getattr(self, 'alias', name)
        return name

    def get_email(self):
        return self.email

    def get_lync(self):
        return self.lync

    def get_role(self, display=False):
        if self.is_administrator():
            self.role = 'administrator'
        elif self.can_submit_commands():
            self.role = 'power'
        else:
            self.role = 'user'

        if display and self.role in self.__class__.roles:
            return self.__class__.roles[self.role]

        return self.role

    def is_anonymous(self):
        """
        Is user anonymous?
        """
        return self.name == 'anonymous'

    def is_administrator(self):
        """
        Is user an administrator?
        """
        if getattr(self, 'back_role_super_admin', None):
            return self.back_role_super_admin
        return self.is_admin

    def can_submit_commands(self):
        """
        Is allowed to use commands?
        """
        if self.is_administrator():
            return True

        if isinstance(self.read_only, bool):
            return not self.read_only
        else:
            return not getattr(self, 'read_only', '0') == '1'

    def can_change_dashboard(self):
        """
        Can the use change dashboard (edit widgets,...)?
        """
        if self.is_administrator():
            return True

        if hasattr(self, 'widgets_allowed'):
            if isinstance(self.widgets_allowed, bool):
                return self.widgets_allowed
            else:
                return getattr(self, 'widgets_allowed', '0') == '1'

        return False

    def is_related_to(self, item):  # pragma: no cover, RFU!
        """ Is the item (host, service, group,...) related to the user?

            In other words, can the user see this item in the WebUI?

            :returns: True or False
        """
        # TODO : to be managed ...
        if item:
            return True

        return False


class LiveSynthesis(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'livesynthesis'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new livesynthesis
        '''
        return super(LiveSynthesis, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a livesynthesis (called only once when an object is newly created)
        '''
        self.linked_host_name = 'host'
        self.linked_service_description = 'service'

        super(LiveSynthesis, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a livesynthesis (called every time an object is updated)
        '''
        super(LiveSynthesis, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a livesynthesis (called every time an object is invoked)
        '''
        super(LiveSynthesis, self).__init__(params)


class LiveState(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'livestate'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new livestate
        '''
        return super(LiveState, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a livestate (called only once when an object is newly created)
        '''
        self.linked_host_name = 'host'
        self.linked_service_description = 'service'

        super(LiveState, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a livestate (called every time an object is updated)
        '''
        super(LiveState, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a livestate (called every time an object is invoked)
        '''
        super(LiveState, self).__init__(params)


class Host(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'host'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new host
        '''
        return super(Host, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a host (called only once when an object is newly created)
        '''
        super(Host, self)._create(params, date_format)


        # Missing in the backend ...
        if not hasattr(self, 'customs'):
            self.customs = []

        # From the livestate
        if not hasattr(self, 'is_impact'):
            self.impact = False
        if not hasattr(self, 'is_problem'):
            self.is_problem = False
        if not hasattr(self, 'problem_has_been_acknowledged'):
            self.problem_has_been_acknowledged = False
        if not hasattr(self, 'last_state_change'):
            self.last_state_change = self._default_date
        if not hasattr(self, 'last_check'):
            self.last_check = self._default_date
        if not hasattr(self, 'output'):
            self.output = self._default_date
        if not hasattr(self, 'long_output'):
            self.long_output = self._default_date
        if not hasattr(self, 'perf_data'):
            self.perf_data = self._default_date
        if not hasattr(self, 'latency'):
            self.latency = self._default_date
        if not hasattr(self, 'execution_time'):
            self.execution_time = self._default_date
        if not hasattr(self, 'attempt'):
            self.attempt = self._default_date
        if not hasattr(self, 'max_check_attempts'):
            self.max_check_attempts = self._default_date
        if not hasattr(self, 'state_type'):
            self.state_type = self._default_date
        if not hasattr(self, 'next_check'):
            self.next_check = self._default_date

        if not hasattr(self, 'comments'):
            self.comments = []

        if not hasattr(self, 'services'):
            self.services = []
        if not hasattr(self, 'downtimes'):
            self.downtimes = []
        if not hasattr(self, 'perfdatas'):
            self.perfdatas = []

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a host (called every time an object is updated)
        '''
        super(Host, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a host (called every time an object is invoked)
        '''
        super(Host, self).__init__(params)


class Service(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'service'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new user
        '''
        return super(Service, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a service (called only once when an object is newly created)
        '''
        super(Service, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a service (called every time an object is updated)
        '''
        super(Service, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a service (called every time an object is invoked)
        '''
        super(Service, self).__init__(params)


class Command(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'command'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new command
        '''
        return super(Command, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a command (called only once when an object is newly created)
        '''
        self.linked_userservice_session = 'userservice_session'
        self.linked_event = 'event'

        super(Command, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a command (called every time an object is updated)
        '''
        super(Command, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a command (called every time an object is invoked)
        '''
        super(Command, self).__init__(params)


# Sort methods
# -----------------------------------------------------
# Sort elements by descending date
def sort_items_most_recent_first(s1, s2):  # pragma: no cover, hard to test ...
    if s1.get_date() > s2.get_date():
        return -1
    if s1.get_date() < s2.get_date():
        return 1
    return 0


# Sort elements by ascending date
def sort_items_least_recent_first(s1, s2):  # pragma: no cover, hard to test ...
    if s1.get_date() < s2.get_date():
        return -1
    if s1.get_date() > s2.get_date():
        return 1
    return 0