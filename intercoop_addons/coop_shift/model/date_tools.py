# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta


def add_days(date_string, days):
    return (
        datetime.strptime(date_string, '%Y-%m-%d').date() +
        timedelta(days=days)).strftime('%Y-%m-%d')


def conflict_period(
        obj1_date_start, obj1_date_stop, obj2_date_start, obj2_date_stop,
        limit_allowed=False):
    """Seen 2 periods ; 2 objects with start dates, and optional stop dates,
    indicate if period are conflicted or not.
    The result is a dict, with the following keys:
        *'conflict': boolean True / False.
        * ('type': type of conflict, of False if periods are not in conflict.)
        * 'date_start': Date of the begin of the conflict.
        * 'date_stop': Date of the end of the conflict.
    param limit_allowed indicated if objX.date_start == objY.date_stop is
    allowed or not.
    """
    def _conflict(date_start, date_stop):
        if not limit_allowed:
            return date_start < date_stop
        else:
            return date_start <= date_stop

    if not obj1_date_stop and not obj2_date_stop:
        # No stop Dates defined
        return {
            'conflict': True,
            'date_start': max(obj1_date_start, obj2_date_start),
            'date_stop': False,
            'type': 'partial',
        }

    if not obj1_date_stop and _conflict(obj1_date_start, obj2_date_stop):
        # Stop date undefined for object 1
        return {
            'conflict': True,
            'date_start': obj2_date_start,
            'date_stop': False,
            'type': 'partial',
        }

    if not obj2_date_stop and _conflict(obj2_date_start, obj1_date_stop):
        # Stop date undefined for object 2
        return {
            'conflict': True,
            'start_date': obj1_date_start,
            'date_stop': False,
            'type': 'partial',
        }

    if (_conflict(obj2_date_start, obj1_date_stop) and
            _conflict(obj1_date_start, obj2_date_stop)):
        # Full superposition
        return {
            'conflict': True,
            'date_start': max(obj1_date_start, obj2_date_start),
            'date_stop': min(obj1_date_stop, obj2_date_stop),
            'type': 'full',
        }

    if (_conflict(obj2_date_start, obj1_date_stop) and
            not _conflict(obj2_date_stop, obj1_date_stop)):
        # Partial conflict on end of obj1
        return {
            'conflict': True,
            'date_start': obj2_date_start,
            'date_stop': obj1_date_stop,
            'type': 'partial',
        }

    if (_conflict(obj1_date_start, obj2_date_stop) and
            not _conflict(obj1_date_stop, obj2_date_stop)):
        # Partial conflict on begin of obj1
        return {
            'conflict': True,
            'date_start': obj1_date_start,
            'date_stop': obj2_date_stop,
            'type': 'partial',
        }
    return {
        'conflict': False,
        'type': 'none',
    }
