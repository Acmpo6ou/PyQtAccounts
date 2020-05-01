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

"""
This module provides all helpful functions and classes that PyQtAccounts uses for updating
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.testutils import QWidget

import git
import os
import threading

from core.const import *
import core.const
from core.utils import *
from core.widgets import *
from urllib.request import urlopen

SRC_DIR = core.const.SRC_DIR


def time_for_updates():
    """
    This function checks whether its time to check for updates or not
    :return:
    bool, True if it is time to check for updates
    """
    # updates check frequency is stored in user settings
    settings = QSettings(f'{os.getenv("HOME")}/PyTools', 'PyQtAccounts')
    # by default we always checking for updates
    frequency = settings.value('updates/frequency', 'always')

    if frequency == 'always':
        # if we always checking for updates we return True
        return True
    else:
        # else we are getting time of the last updates check and current date
        last_checked = settings.value('updates/last', None)
        current = QDate.currentDate()

        # if we never checked for updates yet or we checked but long ago enough we return True
        if not last_checked or last_checked.addDays(frequency.toInt()) <= current:
            settings.setValue('updates/last', current)
            return True
        else:
            # in all other cases (i.e. user has updates check frequency set to `never`) we return
            # False
            return False


def getChangeLog():
    return [change.decode().rstrip() for change in urlopen(
        'https://raw.githubusercontent.com/Acmpo6ou/PyQtAccounts/master/change.log')]


class Updating(QObject):
    result = pyqtSignal(bool, list)

    def run(self):
        import git
        repo = git.Repo('.')
        origin = repo.remote()
        origin.fetch()

        changes = list(repo.iter_commits('master..origin/master'))
        changelog = getChangeLog()

        self.result.emit(bool(changes), changelog)


class UpdatesAvailable(QWidget):
    def __init__(self, parent, log):
        super().__init__()
        self.setParent(parent)
        self.setWindowTitle('Доступно нове оновлення')
        self.setWindowFlags(Qt.Dialog)
        self.resize(1000, 500)
        self.show()

        self.title = Title('<h3>Доступно нове оновлення</h3>')
        self.title.setMinimumWidth(800)
        self.icon = QLabel()
        self.icon.setPixmap(QPixmap('img/update-available.svg'))

        header = QHBoxLayout()
        header.addWidget(self.icon)
        header.addWidget(self.title)

        tip = "Доступно нове оновлення PyQtAccounts.\n" \
              "Після оновлення програма перезапуститься.\n" \
              "Переконайтеся що ви зберігли всі зміни до ваших баз данних перед оновленням.\n"
        self.text = QLabel(tip)
        changelog = '<h4>Що нового:</h4><ul>'
        print(log)
        for change in log:
            changelog += '<li>{}</li>\n'.format(change)
        changelog += '</ul>'
        self.changelogLabel = QLabel(changelog)
        self.changelogLabel.setWordWrap(True)

        self.laterButton = QPushButton('Пізніше')
        self.updateButton = QPushButton('Оновити')
        self.laterButton.clicked.connect(self.hide)
        self.updateButton.clicked.connect(self.applyUpdate)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.laterButton)
        buttonsLayout.addWidget(self.updateButton)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.text)
        layout.addWidget(self.changelogLabel)
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)

    def applyUpdate(self):
        self.hide()
        repo = git.Repo('.')
        origin = repo.remote()
        origin.pull()
        t = threading.Thread(target=os.system, args=('./run.sh',), daemon=True)
        t.start()
        self.parent().close()


class ShowChangelog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Changelog")
        self.resize(800, 500)
        self.show()

        version = getVersion()
        changelog = '<h4>PyQtAccounts {}:</h4><ul>'.format(version)
        for change in open('change.log'):
            changelog += '<li>{}</li>\n'.format(change)
        changelog += '</ul>'
        self.changelogLabel = QLabel(changelog)
        self.changelogLabel.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.changelogLabel)
        self.setLayout(layout)
