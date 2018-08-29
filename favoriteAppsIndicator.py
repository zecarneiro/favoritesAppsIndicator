
# Author: José M. C. Noronha

# Include
import signal
import gi
import json
import threading
import time
from functions import Functions
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

# App Directory
APP_DIR = "/opt/griveIndicator"

class GriveIndicator():
    """
        Init
    """
    def __init__(self):

        # Init functions
        self.functionsClass = Functions(APP_DIR)

        # Icons
        self.iconDefault = "org.gnome.Geary"

        # Other
        self.json_file = "favoritesApps.json"
        self.json_data = self.read_json_file()
        self.applicationID = 'grive_indicator'
        self.manage = None
        self.stop_thread = False
        self.allServiceStoped = False

        print(self.json_data)

        # Define Indicator
        self.indicator = AppIndicator3.Indicator.new(
            self.applicationID,
            self.iconDefault,
            AppIndicator3.IndicatorCategory.OTHER
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Create Set Menu
        self.indicator.set_menu(self.create_menu())

    def read_json_file(self):
        json_file = open(self.json_file, 'r')
        json_data = json.load(json_file)
        return json_data

    def create_sub_menu(self, list_item):
        menu = Gtk.Menu()

        for app in list_item:
            app_item = Gtk.MenuItem(app)
            app_item.connect('activate', self.executeCmd)
            menu.append(app_item)

        menu.show_all()
        return menu

    """
        Create Menu
    """
    def create_menu(self):
        menu = Gtk.Menu()

        for name_menu in self.json_data:
            menu_item = Gtk.MenuItem(name_menu)
            menu_item.set_submenu(self.create_sub_menu(self.json_data[name_menu]))
            menu.append(menu_item)

        item_exitindicator = Gtk.MenuItem('Exit')
        item_exitindicator.connect('activate', self.exit_indicator)
        menu.append(item_exitindicator)
        menu.show_all()
        return menu


    def executeCmd(self, source):
        cmd = "zenity --notification --text=oi"
        self.functionsClass.exec_command(cmd)

    """
        Exit
    """
    def exit_indicator(self, source):
        # Exit Indicator
        Gtk.main_quit()

grive_indicatorClass = GriveIndicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
#GObject.threads_init()
Gtk.main()
