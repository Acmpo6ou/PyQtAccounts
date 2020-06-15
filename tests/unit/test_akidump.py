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

from core.akidump import *
from core.getaki import *

from unittest.mock import Mock
import pytest
import os
import json

from tests.base import UnitTest


class AkidumpTest(UnitTest):
    def setUp(self):
        """
        Here we reassign some widely used variables.
        """
        # Tom has database with gmail account
        account = Account(account='gmail',
                          name='Tom',
                          email='tom@gmail.com',
                          password=b'123',
                          date='01.01.1990',
                          comment='My gmail account.',
                          copy_email=True)
        self.db = {'gmail': account}

    def test_account_serialization(self):
        """
        Here we test how json will serialize our Account class using our
        `to_dict` method that converts our Account instance to dictionary.
        """
        dump = json.dumps(self.db['gmail'].to_dict())
        self.assertEqual(
            dump,
            '{"account": "gmail", "name": "Tom", "email": "tom@gmail.com", '
            '"password": "123", "date": "01.01.1990", '
            '"comment": "My gmail account.", "copy_email": true}',
            '`to_dict` method of Account class is incorrect!')

    def test_dumps(self):
        """
        Here we test dumps function from akidump.py module.
        """

        # here we use dumps function for akidump.py module to serialize his
        # account
        dump = dumps(self.db)
        print(repr(dump))

        # then we check that it is dumped appropriately
        self.assertEqual(
            dump, b'{"gmail": {"account": "gmail", "name": "Tom", "email": '
            b'"tom@gmail.com", "password": "123", "date": "01.01.1990", '
            b'"comment": "My gmail account.", "copy_email": true}}',
            "Serialization of `dumps` function from core.akidump module is incorrect!"
        )

    def test_loads_obsolete(self):
        """
        Here we test how `loads` function from akidump.py module will
        deserialize data that is serialized in obsolete way.
        """
        # we will use openDatabase from core.getaki module which uses loads
        # function from akidump to deserialize database
        db = openDatabase(
            'database',  # `database` serialized in obsolete way
            b'some_password')

        # here we check whether it deserialized appropriately
        # we expect next 3 accounts in deserialized database
        habr = Account(account='habr',
                       name='Lea',
                       email='spheromancer@habr.com',
                       password='habr_password',
                       date='19.05.1990',
                       comment='Habr account.',
                       copy_email=True)
        gmail = Account(account='gmail',
                        name='Bob',
                        email='bobgreen@gmail.com',
                        password='$z#5G_UG~K;I9U9$',
                        date='19.05.1990',
                        comment='Gmail account.',
                        copy_email=True)
        mega = Account(account='mega',
                       name='Tom',
                       email='tom@gmail.com',
                       password='tom',
                       date='01.01.2000',
                       comment='Mega account.',
                       copy_email=True)
        expected_db = {'habr': habr, 'gmail': gmail, 'mega': mega}
        self.assertEqual(db, expected_db)
        # TODO: use isEqual function form utils.py to compare databases
