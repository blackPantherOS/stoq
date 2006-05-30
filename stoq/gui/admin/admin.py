# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s):   Evandro Vale Miquelito      <evandro@async.com.br>
##              Bruno Rafael Garcia         <brg@async.com.br>
##
""" Main gui definition for admin application.  """

import gettext

from kiwi.ui.widgets.list import Column
from sqlobject.sqlbuilder import AND

from stoqlib.gui.base.columns import ForeignKeyColumn
from stoqlib.database import finish_transaction
from stoqlib.lib.runtime import new_transaction
from stoqlib.lib.defaults import ALL_ITEMS_INDEX
from stoqlib.domain.person import Person, PersonAdaptToUser
from stoqlib.domain.profile import UserProfile
from stoqlib.domain.interfaces import IUser
from stoqlib.gui.editors.person import UserEditor
from stoqlib.gui.dialogs.devices import DeviceSettingsDialog
from stoqlib.gui.parameters import ParametersListingDialog
from stoqlib.gui.dialogs.paymentmethod import PaymentMethodsDialog
from stoqlib.gui.search.profile import UserProfileSearch
from stoqlib.gui.wizards.person import run_person_role_dialog
from stoqlib.gui.search.fiscal import CfopSearch, FiscalBookEntrySearch
from stoqlib.gui.search.person import (EmployeeRoleSearch, EmployeeSearch,
                                       BranchSearch)

from stoq.gui.application import SearchableAppWindow
from stoq.lib.applist import get_app_descriptions

_ = gettext.gettext


class AdminApp(SearchableAppWindow):

    app_name = _('Administrative')
    app_icon_name = 'stoq-admin-app'
    gladefile = "admin"
    table = searchbar_table = PersonAdaptToUser
    searchbar_result_strings = (_('user'), _('users'))
    searchbar_labels = (_('matching:'),)
    filter_slave_label = _('Show users with status')
    klist_name = 'users'

    def __init__(self, app):
        SearchableAppWindow.__init__(self, app)
        self._update_view()

    def get_filter_slave_items(self):
        items = [(value, key) for key, value in self.table.statuses.items()]
        items.append((_('Any'), ALL_ITEMS_INDEX))
        return items

    def on_searchbar_activate(self, slave, objs):
        SearchableAppWindow.on_searchbar_activate(self, slave, objs)
        self._update_view()

    def _update_view(self, *args):
        has_selected = self.users.get_selected() is not None
        self.edit_button.set_sensitive(has_selected)
        self.change_password_button.set_sensitive(has_selected)

    def get_columns(self):
        return [Column('username', title=_('Login Name'), sorted=True,
                       data_type=str, width=150, searchable=True),
                ForeignKeyColumn(UserProfile, 'name', title=_('Profile'),
                                 obj_field='profile', data_type=str,
                                 width=150),
                ForeignKeyColumn(Person, 'name', title=_('Name'),
                                 data_type=str, adapted=True,
                                 width=300),
                Column('status_str', title=_('Status'), data_type=str)]

    def _edit_user(self):
        user = self.users.get_selected()
        app_list = get_app_descriptions()
        model =  run_person_role_dialog(UserEditor, self, self.conn,
                                        user, app_list=app_list)
        if finish_transaction(self.conn, model, keep_transaction=True):
            self.users.update(model)

    #
    # Hooks
    #

    def get_extra_query(self):
        """Hook called by SearchBar"""
        q1 = self.table.q._originalID == Person.q.id
        q2 = UserProfile.q.id == self.table.q.profileID
        return AND(q1, q2)

    def filter_results(self, users):
        """Hook called by SearchBar"""
        status = self.filter_slave.get_selected_status()
        if status == ALL_ITEMS_INDEX:
            return users
        elif status == self.table.STATUS_ACTIVE:
            return [user for user in users if user.is_active]
        elif status == self.table.STATUS_INACTIVE:
            return [user for user in users if not user.is_active]
        else:
            raise ValueError('Invalid status for User table. got %s'
                             % status)

    def _add_user(self):
        model = run_person_role_dialog(UserEditor, self, self.conn)
        if finish_transaction(self.conn, model, keep_transaction=True):
            self.searchbar.search_items()
            model = self.table.get(model.id, connection=self.conn)
            self.users.select(model)

    #
    # Callbacks
    #

    def _on_fiscalbook_action_clicked(self, *args):
        self.run_dialog(FiscalBookEntrySearch, self.conn, hide_footer=True)

    def _on_new_user_action_clicked(self, *args):
        self._add_user()

    def on_users__double_click(self, *args):
        self._edit_user()

    def on_users__selection_changed(self, *args):
        self._update_view()

    def _on_cfop_action_clicked(self, *args):
        self.run_dialog(CfopSearch, self.conn, hide_footer=True)

    def _on_employees_action_clicked(self, *args):
        self.run_dialog(EmployeeSearch, self.conn, hide_footer=True)

    def _on_user_profiles_action_clicked(self, *args):
        app_list = get_app_descriptions()
        self.run_dialog(UserProfileSearch, self.conn, app_list)

    def _on_employee_role__action_clicked(self, *args):
        self.run_dialog(EmployeeRoleSearch, self.conn)

    def _on_branch_action_clicked(self, *args):
        self.run_dialog(BranchSearch, self.conn, hide_footer=True)

    def on_add_button__clicked(self, *args):
        self._add_user()

    def on_edit_button__clicked(self, *args):
        self._edit_user()

    def on_change_password_button__clicked(self, *args):
        from stoqlib.gui.editors.person import PasswordEditor
        # This avoid circular import
        user = self.users.get_selected()
        model = self.run_dialog(PasswordEditor, self.conn, user)
        finish_transaction(self.conn, model, keep_transaction=True)

    def on_devices_setup_activate(self, *args):
        self.run_dialog(DeviceSettingsDialog, self.conn)

    def on_system_parameters_activate(self, *args):
        self.run_dialog(ParametersListingDialog, self.conn)

    def on_payment_methods_activate(self, *args):
        self.run_dialog(PaymentMethodsDialog, self.conn)
