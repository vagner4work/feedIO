#!/usr/bin/python
"""
Author  : Chanaka Jayamal
Date    : 20/05/2011
GUI for the feedIO feed aggregator

"""

__version__ = "0.0.1"

__license__ = """
    Copyright (C) 2011 Sri Lanka Institute of Information Technology.

    feedIO is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    feedIO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with feedIO.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Chanaka Jayamal <seejay@seejay.net>"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Chamika Viraj"]


import sys
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import threading
import time

from UI.feedIO_ui import Ui_feedIO
from UI.addFeed_ui import Ui_addFeed
from UI.manageFeeds_ui import Ui_manageFeeds
from UI.removeFeed_ui import Ui_removeFeed
from UI.addTopic_ui import Ui_addTopic
from UI.removeTopic_ui import Ui_removeTopic
from UI.manageTopics_ui import Ui_manageTopics
from UI.about_ui import Ui_About
from UI.license_ui import Ui_License
from UI.credits_ui import Ui_Credits

from UI.systray import SystemTrayIcon
import feedmanager as fm
import classifier

class mainUI(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_feedIO()
        self.ui.setupUi(self)
        self.raise_()

        self.feedList = []
        self.itemList = []
        self.topicList = []

        self.displayTopics()
        self.displayFeeds()
        self.displayItems()

        self.connect(self.ui.comboFeed, SIGNAL("currentIndexChanged(int)"), self.displayItems)
        self.connect(self.ui.listUnread, SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.displayArticle)
        self.connect(self.ui.actionVisitPage, SIGNAL("activated()"), self.visitPage)
        self.connect(self.ui.actionFetchAllFeeds, SIGNAL("activated()"), self.fetchAllFeeds)
#        self.connect(self, SIGNAL('triggered()'), self.closeEvent)

    def closeEvent(self, event):
        """
        Modification to the closeEvent so that pressing the close button in main window will only exit the
        """
        self.hide()
        event.ignore()

    def displayTopics(self):
        self.topicList = classifier.listTopics()
        topicTitles = [topic.title for topic in self.topicList]
        self.ui.comboTopic.clear()
        self.ui.comboTopic.addItems(topicTitles)

    def displayFeeds(self):
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        feedTitles.append("All Feeds")
        self.ui.comboFeed.clear()
        self.ui.comboFeed.addItems(feedTitles)

    def displayItems(self):
        """
        function to update the Articles list according to the selected feeds list.
        """
        selectedIndex = self.ui.comboFeed.currentIndex()

        if len(self.feedList) == 0:
            itemTitles = []
        else:

            if selectedIndex == len(self.feedList):
                self.itemList = fm.listItems()
                itemTitles = [item.title for item in self.itemList]
                windowTitle = "All Feeds - feedIO"
                self.setWindowTitle(windowTitle)
            else:
                selectedFeed = self.feedList[selectedIndex]
                self.itemList = fm.listItems(selectedFeed)
                itemTitles = [item.title for item in self.itemList]
                #Code to change the window title to the currently viewing feed's title
                windowTitle = selectedFeed.title + " - feedIO"
                self.setWindowTitle(windowTitle)
        self.ui.listUnread.clear()
        for article in self.itemList:
#            item=QTreeWidgetItem([article.title, str(time.ctime(article.updated))])
            item=QTreeWidgetItem([article.title,])
            item.article = article

            itemIcon = QIcon()
            itemIcon.addPixmap(QPixmap(":/images/article.png"), QIcon.Normal, QIcon.Off)
            item.setIcon(0, itemIcon)

#            if article.isUnread:
#                item.setCheckState(0,QtCore.Qt.Checked)
#            else:
#                item.setCheckState(0,QtCore.Qt.Unchecked)

            self.ui.listUnread.addTopLevelItem(item)


    def displayArticle(self):
        """
        displays the selected article on the viewer.
        """
        try:
            selected = self.ui.listUnread.currentItem()
            selectedItem = selected.article

            text = "<font face=Georgia>" + "<H3>" + selectedItem.title + \
                "</H3>(" + selectedItem.feed.title + ")<br>" + \
                time.ctime(selectedItem.updated) + "<br>" + \
                selectedItem.description + "</font>"
        except:
            text = "Add some interesting feeds!"
        else:
            self.ui.viewArticle.setHtml(text)
            windowTitle = selectedItem.title + " - " + selectedItem.feed.title + " - feedIO"
            self.setWindowTitle(windowTitle)


    def fetchAllFeeds(self):
        """
        Fetch all action implementataion. Creates a new thread and fetches the updates for them in that thread.
        """

        thread = threading.Thread(target=fm.updateAll, args=())
        thread.start()


    def  visitPage(self):
        """
        function to visit the original web page of selected article from the built in web browser.
        """
        try:
            selected = self.ui.listUnread.currentItem()
        except:
            text = "Not implemented yet."
        else:
            self.ui.viewArticle.load(QUrl(selected.article.url))


    def on_actionManageFeeds_activated(self, i = None):
        """
        Manage feeds action implementataion. displays the manageFeeds dialog box.
        """
        if i is None: return
        ManageFeedsDialog(self).exec_()
        self.displayFeeds()


    def on_actionAddFeed_activated(self, i = None):
        if i is None: return

        AddFeedDialog(self).exec_()
        self.displayFeeds()

    def on_actionRemoveFeed_activated(self, i = None):
        if i is None: return

        RemoveFeedDialog(self).exec_()
        self.displayFeeds()


    def on_actionManageTopics_activated(self, i = None):
        """
        Manage feeds action implementataion. displays the manageFeeds dialog box.
        """
        if i is None: return

        ManageTopicsDialog(self).exec_()
        self.displayTopics()


    def on_actionAddTopic_activated(self, i = None):
        if i is None: return

        AddTopicDialog(self).exec_()
        self.displayTopics()


    def on_actionRemoveTopic_activated(self, i = None):
        if i is None: return

        RemoveTopicDialog(self).exec_()
        self.displayTopics()


    def on_actionExit_activated(self, i = None):
        """
        Exit action implementataion. Exits the application.
        """
        if i is None: return
        self.parent.close()

    def on_actionMinimizeToTray_activated(self, i = None):
        """
        Exit action implementataion. Exits the application.
        """
        if i is None: return
        self.close()

    def on_actionAbout_activated(self, i = None):
        """
        About action implementataion.
        """
        if i is None: return
        AboutDialog(self).exec_()


class AddFeedDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addFeed()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnAdd, SIGNAL("clicked()"), self.addFeed)
        self.connect(self.ui.UrlLineEdit, SIGNAL("returnPressed()"), self.addFeed)

    def addFeed(self):
        feedUrl = unicode(self.ui.UrlLineEdit.text())

        thread = threading.Thread(target=fm.addFeed, args=(feedUrl,))
        thread.setDaemon(True)
        thread.start()

        thread.join()
        self.close()


class RemoveFeedDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_removeFeed()
        self.ui.setupUi(self)
        self.feedList = []
        self.displayFeeds()

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL("clicked()"), self.removeFeed)

    def displayFeeds(self):
        """
        function to display the subscribed feeds list in the combo box.
        """
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        self.ui.feedList.clear()
        self.ui.feedList.addItems(feedTitles)

    def removeFeed(self):
        selectedIndex = self.ui.feedList.currentIndex()
        selectedFeed = self.feedList[selectedIndex]
        fm.removeFeed(selectedFeed)
        self.close()


class ManageFeedsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_manageFeeds()
        self.ui.setupUi(self)
        self.feedList = []
        self.displayFeeds()

        self.connect(self.ui.btnExit, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL('clicked()'), self.removeFeed)
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addFeed)

    def displayFeeds(self):
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        self.ui.feedList.clear()
        self.ui.feedList.addItems(feedTitles)

    def removeFeed(self):
        selectedItemIndex = self.ui.feedList.currentRow()
        selectedFeed = self.feedList[selectedItemIndex]
        fm.removeFeed(selectedFeed)
        self.displayFeeds()

    def addFeed(self):
        feedUrl = unicode(self.ui.urlLine.text())
        #Run the addFeed function in a new thread so that the ui is responsive.
        thread = threading.Thread(target=fm.addFeed, args=(feedUrl,))
        thread.setDaemon(True)
        thread.start()
        thread.join()
        self.ui.urlLine.clear()
        self.displayFeeds()


class AddTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addTopic()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addTopic)

    def addTopic(self):
        topic = unicode(self.ui.addTopicLinedit.text())
        classifier.addTopic(topic)
        self.close()


class RemoveTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_removeTopic()
        self.ui.setupUi(self)

        self.topicList = []
        self.displayTopics()

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL("clicked()"), self.removeTopic)

    def displayTopics(self):
        """
        function to display the current topics list in the combo box.
        """
        self.topicList = classifier.listTopics()
        self.topicList.remove(classifier.getTopic("General"))
        topicTitles = [topic.title for topic in self.topicList]
        self.ui.topicListCombo.clear()
        self.ui.topicListCombo.addItems(topicTitles)

    def removeTopic(self):
        selectedIndex = self.ui.topicListCombo.currentIndex()
        selectedTopic = self.topicList[selectedIndex]
        classifier.removeTopic(selectedTopic)
        self.close()


class ManageTopicsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_manageTopics()
        self.ui.setupUi(self)
        self.topicList = []
        self.displayTopics()

        self.connect(self.ui.btnExit, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL('clicked()'), self.removeTopic)
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addTopic)

    def displayTopics(self):
        self.topicList = classifier.listTopics()
        self.topicList.remove(classifier.getTopic("General"))
        topicTitles = [topic.title for topic in self.topicList]
        self.ui.topicList.clear()
        self.ui.topicList.addItems(topicTitles)

    def removeTopic(self):
        selectedItemIndex = self.ui.topicList.currentRow()
        selectedTopic = self.topicList[selectedItemIndex]
        classifier.removeTopic(selectedTopic)
        self.displayTopics()

    def addTopic(self):
        topic = unicode(self.ui.topicLine.text())
        classifier.addTopic(topic)
        self.ui.topicLine.clear()
        self.displayTopics()


class AboutDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_About()
        self.ui.setupUi(self)

        self.connect(self.ui.btnClose, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnLicense, SIGNAL('clicked()'), self.loadLicense)
        self.connect(self.ui.btnCredits, SIGNAL('clicked()'), self.loadCredits)

    def loadLicense(self):
        LicenseDialog(self).exec_()

    def loadCredits(self):
        CreditsDialog(self).exec_()

class LicenseDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_License()
        self.ui.setupUi(self)

        self.connect(self.ui.btnClose, SIGNAL('clicked()'), SLOT('close()'))

class CreditsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_Credits()
        self.ui.setupUi(self)

        self.connect(self.ui.btnClose, SIGNAL('clicked()'), SLOT('close()'))


def initUI():

    app = QApplication(sys.argv)
    #Splash screen implementation
    splash_pix = QPixmap(":/images/splash.png")
#    splash_pix = QPixmap('./images/feedIO-splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())

    splash.show()
    app.processEvents()

#    time.sleep(2)

    # create a feedIO QWidget instance
    feedIO = QWidget()

    # pass feedIO as the parent for the mainWindow.
    mainWindow = mainUI(feedIO)

    # system tray icon
    icon = QIcon()
    icon.addPixmap(QPixmap(":/images/feedIO.png"), QIcon.Normal, QIcon.Off)

    # Pass the feedIO instance as the parent and the mainWindow instance as the child.
    trayIcon = SystemTrayIcon(icon, feedIO, mainWindow)

    #tool tip for the system try icon.
    # TODO this should be updated appropriately at run time.
    trayIcon.setToolTip("feedIO " + __version__ + " developer build running...")
    trayIcon.show()

    mainWindow.show()
    splash.finish(mainWindow)
    sys.exit(app.exec_())


if __name__ == "__main__":
    initUI()