# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2007 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
##
""" Routines for system data management"""

from stoqlib.database.orm import DateTimeCol, IntCol
from stoqlib.database.orm import ORMObject


class SystemTable(ORMObject):
    """Stores information about database schema migration

    I{update}: the date when the database schema was updated
    I{patchlevel}: the version of the schema installed
    """
    __storm_table__ = 'system_table'

    updated = DateTimeCol()
    patchlevel = IntCol()
    generation = IntCol()

    @classmethod
    def is_available(cls, store):
        """Checks if Stoqlib database is properly installed
        :param store: a store
        """
        if not store.table_exists('system_table'):
            return False

        return bool(store.find.select(cls))


class TransactionEntry(ORMObject):
    """
    A TransactionEntry keeps track of state associated with a database
    transaction. It's main use case is to know information about the system when
    a domain object is created or modified.
    """
    __storm_table__ = 'transaction_entry'

    (CREATED,
     MODIFIED) = range(2)

    te_time = DateTimeCol(allow_none=False)

    # This is used by base classes in Stoq, ORMObject does not allow
    # us to use circular dependencies so instead we define them
    # as IntCol and implement our own wrappers below
    user_id = IntCol(default=None) # a LoginUser foreign key
    station_id = IntCol(default=None) # a BranchStation foreign key

    #: if it represents a creation or modification
    type = IntCol()

    @property
    def user(self):
        """Returns the user associated with the TransactionEntry"""
        if not self.user_id:
            return
        from stoqlib.domain.person import LoginUser
        return LoginUser.get(self.user_id,
                             store=self.store)

    @property
    def station(self):
        """Returns the station associated with the TransactionEntry"""
        if not self.station_id:
            return
        from stoqlib.domain.station import BranchStation
        return BranchStation.get(self.station_id,
                                 store=self.store)
