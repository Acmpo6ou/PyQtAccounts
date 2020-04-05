#!/usr/bin/env python3

# Copyright (c) 2020 Kolvakh B.
# This file is part of PyQtAccounts.

# PyQtAccounts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PyQtAccounts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PyQtAccounts.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtTest import QTest
from PyQt5.QtCore import *
import unittest
import pytest
import os

from tests.base import AccsTest
from core.utils import *
from PyQtAccounts import *
from tests.func.test_import_export import ImportExportTest


class DbSaveTest(AccsTest):
    def setUp(self):
        super().setUp('import_database', 'import_database')
        self.form = self.accs.forms['edit']
        self.list = self.accs.list
        self.saveButton = self.form.createButton
        self.editButton = self.accs.panel.editButton
        self.name = self.form.nameInput
        self.email = self.form.emailInput

        self.save_db = open('src/import_database.db', 'rb').read()

    def tearDown(self):
        open('src/import_database.db', 'wb').write(self.save_db)

    def openDatabase(self):
        window = Window()
        dbs = window.dbs
        form = dbs.forms['open']
        _list = dbs.list
        pass_input = form.passField.passInput
        _list.selected(Index('import_database'))
        pass_input.setText('import_database')
        form.openButton.click()
        win = window.windows[1]
        accs = win.accs
        return win

    def test_save_after_edit(self):
        # Ross wants to edit his account, so he chose it in the list and presses edit button
        self.list.selected(Index('firefox'))
        self.editButton.click()

        # He change account nickname and presses save button of edit form
        self.name.setText('Ross Geller')
        self.saveButton.click()

        # Ross then goes to menu: File -> Save
        file = self.win.menuBar().actions()[0]  # first is `File` submenu
        save = file.menu().actions()[1]         # second action is `Save`
        save.trigger()

        # Database is saved now, so he closes the database window, and there is no messages
        self.win.close()
        self.assertNotIn(self.win, self.window.windows)
        self.window.close()
        del self.window

        # Ross then opens database again to check is everything saved
        win = self.openDatabase()
        accs = win.accs

        # He chose his account at the list
        accs.list.selected(Index('firefox'))

        # And he sees his name changed at the account show form
        self.assertEqual("Ім'я: Ross Geller", accs.forms['show'].name.text())

    def test_save_message_Yes(self):
        # Lea wants to edit her account, so she chose it in the list
        self.list.selected(Index('firefox'))
        self.editButton.click()

        # She change her e-mail to `spam@python.org` and presses save button
        self.email.setText('spam@python.org')
        self.saveButton.click()

        # But then Lea changed her mind and closes database window
        # Message appears asking her about unsaved changes
        # Lea presses `Yes`
        self.monkeypatch.setattr(QMessageBox, 'question', self.mess(
            'Увага!',
            'Ви певні що хочете вийти?\n'
            'Усі незбережені зміни буде втрачено!\n'
            'Натисніть Ctrl+S аби зберегти зміни.', button=QMessageBox.Yes))
        self.win.close()

        # Database window is closed now and Lea closes PyQtAccounts
        self.assertNotIn(self.win, self.window.windows)
        self.window.close()
        del self.window

        # She then opens database again to check that changes aren't saved
        win = self.openDatabase()
        accs = win.accs

        # She chose her account in the list
        accs.list.selected(Index('firefox'))

        # And sees that her e-mail is such as it was
        self.assertEqual("E-mail: firefox@gmail.com", accs.forms['show'].email.text())

    def test_save_message_No(self):
        # Lea wants to edit her account again, so she chose it in the list
        self.list.selected(Index('firefox'))
        self.editButton.click()

        # She change her e-mail to `spam@python.org` and presses save button
        self.email.setText('spam@python.org')
        self.saveButton.click()

        # But then Lea changed her mind and closes database window
        # Message appears asking her about unsaved changes
        # Lea presses `No`
        self.monkeypatch.setattr(QMessageBox, 'question', self.mess(
            'Увага!',
            'Ви певні що хочете вийти?\n'
            'Усі незбережені зміни буде втрачено!\n'
            'Натисніть Ctrl+S аби зберегти зміни.', button=QMessageBox.No))
        self.win.close()

        # Database window is still opened
        self.assertIn(self.win, self.window.windows)

        # Lea then change her e-mail back to `firefox@gmail.com` as it was and saves it
        self.email.setText('firefox@gmail.com')
        self.saveButton.click()

        # Then she closes database window and there is now messages
        self.monkeypatch.setattr(QMessageBox, 'question', self.mess_showed)