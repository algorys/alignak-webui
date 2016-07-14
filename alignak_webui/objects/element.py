#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Many functions need to use protected members of a base class
# pylint: disable=protected-access
# Attributes need to be defined in constructor before initialization
# pylint: disable=attribute-defined-outside-init

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
    This module contains the base class used to manage the application objects
    with the data manager.
"""

import time
from calendar import timegm
from datetime import datetime
from logging import getLogger, INFO

# noinspection PyProtectedMember
from alignak_webui import get_app_config, _
# Import the backend interface class
from alignak_webui.objects.backend import BackendConnection
from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.helper import Helper

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
logger.setLevel(INFO)


class BackendElement(object):
    # Yes, but it is the base object and it needs those pubic methods!
    # pylint: disable=too-many-public-methods
    """
    Base class for all the data manager objects

    An Item is created from a dictionary with some specific features:
    - an item has an identifier, a name, an alias and a comment (notes)
    - some specific treatments are applied on some specific fields (see _create method doc)
    - all objects are cached internally to avoid creating several instances for the same element

    If no identifier attribute exists in the provided data an automatic identifier is assigned.

    Manages links between Item objects base upon some specific fields.

    !!!!! TO BE COMPLETED !!!!!
    """
    _count = 0
    _total_count = -1

    _backend = None
    _known_classes = None

    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'item'
    # _cache is a list of created objects
    _cache = {}

    # Default date used for bad formatted string dates
    _default_date = 0

    # Dates fields: list of the attributes to be considered as dates
    _dates = ['_created', '_updated']

    _name = 'anonymous'
    _alias = ''
    _status = 'unknown'
    _notes = ''

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

    @classmethod
    def get_known_classes(cls):
        """ Get protected member """
        return cls._known_classes

    @classmethod
    def set_known_classes(cls, known_classes):
        """ Set protected member _known_classes """
        cls._known_classes = known_classes

    @classmethod
    def get_backend(cls):
        """ Get protected member """
        return cls._backend

    @classmethod
    def set_backend(cls, backend):
        """ Set protected member _backend """
        cls._backend = backend

    @classmethod
    def get_type(cls):
        """ Get protected member """
        return cls._type

    @classmethod
    def get_count(cls):
        """ Get protected member """
        return cls._count

    @classmethod
    def get_total_count(cls):
        """ Get protected member """
        return cls._total_count

    @classmethod
    def set_total_count(cls, count):
        """ Set protected member _total_count """
        cls._total_count = count

    @classmethod
    def get_cache(cls):
        """ Get protected member """
        return cls._cache

    @classmethod
    def clean_cache(cls):
        """
        Clean internal objects cache and reset the internal counters
        """
        cls._next_id = 1
        cls._count = 0
        cls._total_count = -1
        cls._cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
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
        """
        id_property = getattr(cls, 'id_property', '_id')
        # print "Class %s, id_property: %s, params: %s" % (cls, id_property, params)

        if not cls.get_backend():
            # Get global configuration
            app_config = get_app_config()
            if not app_config:  # pragma: no cover, should not happen
                return

            cls._backend = BackendConnection(
                app_config.get('alignak_backend', 'http://127.0.0.1:5000')
            )
            # print "Class backend: %s" % (cls.get_backend())

        _id = '0'
        if params:
            if not isinstance(params, dict):
                logger.warning(
                    "Class %s, id_property: %s, invalid params: %s",
                    cls, id_property, params
                )
                if isinstance(params, BackendElement):
                    params = params.__dict__
                else:
                    logger.critical(
                        "Class %s, id_property: %s, invalid params: %s",
                        cls, id_property, params
                    )
                    raise ValueError(
                        '%s.__new__: object parameters must be a dictionary!' % (
                            cls._type
                        )
                    )

            if id_property in params:
                if not isinstance(params[id_property], basestring):
                    params[id_property] = str(params[id_property])
                _id = params[id_property]
            else:
                _id = '%s_%d' % (cls.get_type(), cls._next_id)
                params[id_property] = _id
                cls._next_id += 1

        if _id == '0':
            if not params:
                params = {}
            # Force _id in the parameters
            params.update({id_property: '%s_0' % (cls.get_type())})

        if _id not in cls._cache:
            # print "Create a new %s (%s)" % (cls.get_type(), _id)
            cls._cache[_id] = super(BackendElement, cls).__new__(cls, params, date_format)
            cls._cache[_id]._type = cls.get_type()
            cls._cache[_id]._default_date = cls._default_date
            # print " ... new: %s" % cls._cache[_id]

            # Call the new object create function
            cls._cache[_id]._create(params, date_format)
            # print " ... created: %s" % cls._cache[_id]
            cls._count += 1
        else:
            if params != cls._cache[_id].__dict__:
                # print "Update existing instance for: ", cls._cache[_id]
                cls._cache[_id]._update(params, date_format)

        return cls._cache[_id]

    def __del__(self):
        """
        Delete an object (called only when no more reference exists for an object)
        """
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)

    def _delete(self):
        """
        Delete an object

        If the object exists in the cache, its reference is removed from the internal cache.
        """
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)
        cls = self.__class__
        if self._id in cls._cache:
            logger.debug("Removing from cache...")
            del cls._cache[self._id]
            cls._count -= 1
            logger.debug(
                "Removed. Remaining in cache: %d / %d",
                cls.get_count(), len(cls.get_cache())
            )

    def _create(self, params, date_format):
        """
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
            If the object has declared some '_linked_XXX' prefixed attributes and the paramaters
            contain an 'XXX' field, this function creates a new object in the '_linked_XXX'
            attribute. The initial '_linked_XXX' attribute must contain the new object type!

            If the attribute is a simple dictionary, the new attribute contains the dictionary.

            This feature allows to create links between embedded objects of the backend.
        """
        id_property = getattr(self.__class__, 'id_property', '_id')
        if id_property not in params:  # pragma: no cover, should never happen
            raise ValueError('No %s attribute in the provided parameters' % id_property)
        logger.debug(
            " --- creating a %s (%s - %s)",
            self.get_type(), params[id_property], params['name'] if 'name' in params else ''
        )

        for key in params:  # pylint: disable=too-many-nested-blocks
            logger.debug(" parameter: %s (%s) = %s", key, params[key].__class__, params[key])
            # print(" parameter: %s (%s) = %s", key, params[key].__class__, params[key])
            # Object must have declared a _linked_ attribute ...
            if hasattr(self, '_linked_' + key) and self.get_known_classes():
                logger.debug(
                    " link parameter: %s (%s) = %s", key, params[key].__class__, params[key]
                )
                # Linked resource type
                object_type = getattr(self, '_linked_' + key, None)
                if object_type not in [kc.get_type() for kc in self.get_known_classes()]:
                    logger.error("_create, unknown %s for %s", object_type, params[key])
                    continue

                object_class = [kc for kc in self.get_known_classes()
                                if kc.get_type() == object_type][0]

                # Dictionary - linked object attributes (backend embedded object)
                if isinstance(params[key], dict):
                    linked_object = object_class(params[key])
                    setattr(self, '_linked_' + key, linked_object)
                    logger.debug("_create, linked with %s (%s)", key, linked_object['_id'])
                    continue

                # String - object id
                if isinstance(params[key], basestring) and self.get_backend():
                    # we need to load the object from the backend
                    result = self.get_backend().get(object_type + '/' + params[key])
                    if not result:
                        logger.error(
                            "_create, item not found for %s, %s", object_type, params[key]
                        )
                        continue

                    # Create a new object
                    linked_object = object_class(result)
                    setattr(self, '_linked_' + key, linked_object)
                    logger.debug("_create, linked with %s (%s)", key, linked_object['_id'])
                    continue

                # List - list of objects id
                if isinstance(params[key], list):
                    objects_list = []
                    for element in params[key]:
                        if isinstance(element, basestring) and self.get_backend():
                            # we need to load the object from the backend
                            result = self.get_backend().get(object_type + '/' + element)
                            if not result:
                                logger.error(
                                    "_create, item not found for %s, %s", object_type, params[key]
                                )
                                continue

                            # Create a new object
                            objects_list.append(object_class(result))
                        elif isinstance(element, dict):
                            # Create a new object from a dict
                            objects_list.append(object_class(element))
                        else:
                            logger.critical(
                                "_create, list element %s is not a string nor a dict: %s",
                                key, element
                            )

                    setattr(self, '_linked_' + key, objects_list)
                    logger.debug("_create, linked with %s (%s)", key, [o for o in objects_list])
                    continue

                logger.debug(
                    "Parameter: %s for %s is not a dict or a list or an object id "
                    "as it should be, instead of being: %s",
                    key, self.get_type(), params[key]
                )
                continue

            # If the property is a known date, make it a timestamp...
            if key.endswith('date') or key in self.__class__._dates:
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

            # noinspection PyBroadException
            try:
                setattr(self, key, params[key])
            except Exception:
                logger.critical("_create parameter TypeError: %s = %s", key, params[key])

        # Object name
        if not hasattr(self, 'name'):
            setattr(self, 'name', 'anonymous')

        # Object alias
        if not hasattr(self, 'alias'):
            setattr(self, 'alias', '')

        # Object notes
        if not hasattr(self, 'notes'):
            setattr(self, 'notes', '')

        # Object status
        if not hasattr(self, 'status'):
            setattr(self, 'status', 'unknown')

        logger.debug(" --- created %s (%s): %s", self.__class__, self[id_property], self.__dict__)

    def _update(self, params, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        # pylint: disable=too-many-nested-blocks
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- updating a %s (%s)", self.object_type, self[id_property])

        if not isinstance(params, dict):
            if self.__class__ == params.__class__:
                params = params.__dict__
            elif self.get_known_classes() and params.__class__ in self.get_known_classes():
                params = params.__dict__
            else:
                logger.debug(
                    "_update, cannot update an object (%s) with: %s (%s)"
                    "Updated object is a second level object, else "
                    "you should try to embed this object from the backend",
                    self.__class__, params, params.__class__
                )
                return

        for key in params:
            logger.debug(" --- parameter %s = %s", key, params[key])
            if hasattr(self, '_linked_' + key):
                logger.debug(
                    "link parameter: %s (%s) = %s", key, params[key].__class__, params[key]
                )
                object_type = getattr(self, '_linked_' + key, None)

                # Already contains an object, so update object ...
                if isinstance(object_type, BackendElement):
                    logger.debug("_update, update object: %s = %s", key, params[key])
                    object_type._update(params[key])
                    continue

                # Linked resource type
                logger.debug(
                    "_update, must create a link for %s -> %s with %s ",
                    self.object_type, key, params[key]
                )

                if isinstance(object_type, list):
                    # Some objects are linked through a list
                    if not object_type:
                        logger.debug("_update, empty list")
                        continue
                    object_class = object_type[0].__class__
                    object_type = object_type[0].get_type()

                elif object_type in [kc.get_type() for kc in self.get_known_classes()]:
                    # No object yet linked... find its class thanks to the known type
                    object_class = [kc for kc in self.get_known_classes()
                                    if kc.get_type() == object_type][0]
                else:
                    logger.error("_update, unknown %s for %s", object_type, params[key])
                    continue

                # String - object id
                if isinstance(params[key], basestring) and self.get_backend():
                    # Object link is a string, so it contains the object type
                    object_type = getattr(self, '_linked_' + key, None)
                    if object_type not in [kc.get_type() for kc in self.get_known_classes()]:
                        logger.error("_update, unknown %s for %s", object_type, params[key])
                        continue

                    object_class = [kc for kc in self.get_known_classes()
                                    if kc.get_type() == object_type][0]

                    # Object link is a string, so we need to load the object from the backend
                    result = self.get_backend().get(object_type + '/' + params[key])
                    if not result:
                        logger.error(
                            "_update, item not found for %s, %s", object_type, params[key]
                        )
                        continue

                    # Create a new object
                    linked_object = object_class(result)
                    setattr(self, '_linked_' + key, linked_object)
                    logger.warning("_update, linked with %s (%s)", key, linked_object['_id'])
                    continue

                # List - list of objects id
                if isinstance(params[key], list):
                    objects_list = []
                    for element in params[key]:
                        if isinstance(element, basestring) and self.get_backend():
                            # we need to load the object from the backend
                            result = self.get_backend().get(object_type + '/' + element)
                            if not result:
                                logger.error(
                                    "_update, item not found for %s, %s", object_type, params[key]
                                )
                                continue

                            # Create a new object
                            objects_list.append(object_class(result))
                        elif isinstance(element, dict):
                            # Create a new object from a dict
                            objects_list.append(object_class(element))
                        else:
                            logger.critical(
                                "_update, list element %s is not a string nor a dict: %s",
                                key, element
                            )

                    setattr(self, '_linked_' + key, objects_list)
                    logger.info("_update, linked with %s (%s)", key, [o for o in objects_list])
                    continue

                continue

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in self.__class__._dates:
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
                logger.critical("_update, parameter TypeError: %s = %s", key, params[key])

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Initialize an object

        Beware: always called, even if the object is not newly created! Use _create function for
        initializing newly created objects.
        """
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- initializing a %s (%s)", self._type, self[id_property])
        logger.debug(" --- initializing with %s and %s", params, date_format)

    def __repr__(self):
        return "<%s, id: %s, name: %s, status: %s>" % (
            self.__class__._type, self.id, self.name, self.status
        )

    def __getitem__(self, key):
        return getattr(self, key, None)

    @property
    def object_type(self):
        """
        Get Item object type
        """
        return self._type

    @property
    def id(self):
        """
        Get Item object identifier
        A class inheriting from an Item can define its own `id_property`
        """
        if hasattr(self.__class__, 'id_property'):
            return getattr(self, self.__class__.id_property, None)
        return self._id

    @property
    def name(self):
        """
        Get Item object name
        A class inheriting from an Item can define its own `name_property`
        """
        if hasattr(self.__class__, 'name_property'):
            return getattr(self, self.__class__.name_property, None)
        return self._name

    @property
    def endpoint(self):
        """
        Get Item endpoint (page url)
        """
        return '/%s/%s' % (self.object_type, self.id)

    @property
    def html_link(self):
        """
        Get Item html link
        """
        return '<a href="%s">%s</a>' % (self.endpoint, self.alias)

    def get_html_link(self, prefix=None):
        """
        Get Item html link with an optional prefix
        """
        if prefix:
            return '<a href="%s%s">%s</a>' % (prefix, self.endpoint, self.alias)
        return self.html_link

    @property
    def html_state_link(self):
        """
        Get Item html link with state
        """
        return '<a href="%s">%s</a>' % (self.endpoint, self.get_html_state(
            text=self.alias, title=self.alias
        ))

    def get_html_state_link(self, prefix=None):
        """
        Get Item html link with state and an optional prefix
        """
        if prefix:
            return '<a href="%s%s">%s</a>' % (prefix, self.endpoint, self.get_html_state(
                text=self.alias, title=self.alias
            ))
        return self.html_state_link

    @name.setter
    def name(self, name):
        """
        Set Item object name
        """
        if hasattr(self.__class__, 'name_property'):
            setattr(self, self.__class__.name_property, name)
        else:
            self._name = name

    @property
    def alias(self):
        """
        Get Item object alias
        A class inheriting from an Item can define its own `name_property`
        """
        if hasattr(self, 'alias') and getattr(self, '_alias', None):
            return getattr(self, '_alias', None)
        return getattr(self, 'name', '')

    @alias.setter
    def alias(self, alias):
        """
        Set Item object alias
        """
        self._alias = alias

    @property
    def notes(self):
        """
        Get Item object notes
        A class inheriting from an Item can define its own `comment_property`
        """
        if hasattr(self.__class__, 'comment_property'):
            return getattr(self, self.__class__.comment_property, None)
        return self._notes

    @notes.setter
    def notes(self, notes):
        """
        Get Item object notes
        A class inheriting from an Item can define its own `comment_property`
        """
        if hasattr(self.__class__, 'comment_property'):
            setattr(self, self.__class__.comment_property, notes)
        else:
            self._notes = notes

    @property
    def status(self):
        """
        Get Item object status
        A class inheriting from an Item can define its own `status_property`
        """
        if hasattr(self.__class__, 'status_property'):
            return getattr(self, self.__class__.status_property, None)
        return self._status

    @status.setter
    def status(self, status):
        """
        Get Item object status
        A class inheriting from an Item can define its own `status_property`
        """
        if hasattr(self.__class__, 'status_property'):
            setattr(self, self.__class__.status_property, status)
        else:
            self._status = status

    def get_state(self):
        """
        Get Item object state
        A class inheriting from an Item can define its own `state_property`

        !!!!! TO BE COMPLETED !!!!
        """
        state = getattr(self, 'state', 99)
        if isinstance(state, int):
            try:
                return self.__class__.items_states[state]
            except IndexError:
                return ''
        return state

    def get_icon_states(self):
        """
        Uses the ElementState singleton to get configured states for an item
        """
        return ElementState().get_icon_states()

    def get_html_state(self, extra='', icon=True, text='',
                       title='', disabled=False, object_type=None, object_item=None,
                       size=''):
        # pylint: disable=too-many-arguments
        """
        Uses the ElementState singleton to display HTML state for an item
        """
        if not object_type:
            object_type = self.object_type

        if not object_item:
            object_item = self

        return ElementState().get_html_state(object_type, object_item,
                                             extra, icon, text, title, disabled, size)

    def get_date(self, _date, fmt=None, duration=False):
        """
        Format the provided `_date` as a string according to the specified format.

        If no date format is specified, it uses the one defined in the ElementState object that is
        the date format defined in the application configuration.

        If duration is True, the date is displayed as a pretty date: 1 day 12 minutes ago ...
        """
        if _date == self.__class__._default_date:
            return _('Never dated!')

        if duration:
            return Helper.print_duration(_date, duration_only=False, x_elts=0)

        item_state = ElementState()
        if not fmt:
            if item_state.date_format:
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