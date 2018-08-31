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
from gi.repository import Gtk, AppIndicator3, GObject

# App Directory
APP_DIR = "/opt/favoritesAppsIndicator"


class FavoritesAppsIndicator:
    """
        Init
    """
    def __init__(self):

        # Init functions
        self.functionsClass = Functions(APP_DIR)

        # Get home path
        self.home = self.functionsClass.exec_command_get_output("echo $HOME")
        self.configDir = self.home + "/.config/favoritesAppsIndicator"

        # Icons
        self.iconDefault = APP_DIR + "/icon/favoritesApps.png"

        # List path for desktop files
        self.path_desktop_files = [
            "/usr/share/applications/",  # System directory
            self.home + "/.local/share/applications/",  # User local directory
            "/var/lib/flatpak/exports/share/applications/",  # Flatpak
            "/var/lib/snapd/desktop/applications/"  # Snap
        ]

        # Other
        self.applicationID = 'favorites_apps_indicator'
        self.zenity_cmd = "zenity --notification --window-icon=\"" + self.iconDefault + "\" --text="
        self.stop_thread = False

        # Read Json File
        self.json_file = self.configDir + "/favoritesApps.json"
        self.json_data = self.read_json_file()
        self.cmd_stat_json_file = "stat -c '%y' \"" + self.json_file + "\""
        self.stats_config_file = self.functionsClass.exec_command_get_output(self.cmd_stat_json_file)

        # Define Indicator
        self.indicator = AppIndicator3.Indicator.new(
            self.applicationID,
            self.iconDefault,
            AppIndicator3.IndicatorCategory.OTHER
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # start service
        self.start_service_update_menu()

        # Create Set Menu
        self.indicator.set_menu(self.create_menu())

    """
        Read JSON File
    """
    def read_json_file(self):
        if self.functionsClass.checkFileExist(self.json_file):
            json_file = open(self.json_file, 'r')
            json_data = json.load(json_file)
            return json_data
        else:
            msg = "\"JSON File not exist\""
            self.functionsClass.exec_command(self.zenity_cmd + msg)
            self.exit_indicator(None)

    """
        Verify is desktop file exist or not
    """
    def is_desktop_file_exist(self, desktop_file):
        for path in self.path_desktop_files:
            file = path + desktop_file
            if self.functionsClass.checkFileExist(file):
                return file

        # Return false desktop file not exist
        return False

    """
        Launch desktop file
    """
    def lauch_desktop(self, source, command):
        cmd_to_launch = command + " &"
        self.functionsClass.exec_command(cmd_to_launch)

    """
        Return Icon from desktop files
    """
    def get_icon(self, desktop_file):
        file = self.is_desktop_file_exist(desktop_file)
        if file:
            # Command to get icon
            cmd = "cat \"" + file + "\" | grep \"Icon=\" | cut -d \"=\" -f2"

            # Init Image Gtk
            image = Gtk.Image()

            # Get icon
            icon = self.functionsClass.exec_command_get_output(cmd)

            # Select type of icon
            if self.functionsClass.checkFileExist(icon):
                image.set_from_file(icon)
            else:
                image.set_from_icon_name(icon, Gtk.IconSize.MENU)

            # Return image
            return image

    """
        Return Icon from desktop files
    """
    def get_command(self, desktop_file):
        file = self.is_desktop_file_exist(desktop_file)
        if file:
            # Command to get lounch

            # Get icon
            command = "gtk-launch \"" + desktop_file + "\""

            # Return image
            return command


    """
        Return name app from desktop files
    """
    def get_app_name(self, desktop_file):
        file = self.is_desktop_file_exist(desktop_file)
        name = None
        if file:
            # Command to get name
            cmd = "cat \"" + file + "\" | grep \"Name=\" | cut -d \"=\" -f2"
            cmd_full_lines = "cat \"" + file + "\" | grep \"Name=\""
            cmd_count = "cat \"" + file + "\" | grep -c \"Name=\" | cut -d \"=\" -f2"

            # Get name
            if int(self.functionsClass.exec_command_get_output(cmd_count)) > 1:
                # Get full lines with names
                string_full_lines = self.functionsClass.exec_command_get_output(cmd_full_lines)
                array_full_lines = string_full_lines.split('\n')

                # Get names
                string_names = self.functionsClass.exec_command_get_output(cmd)
                array_name = string_names.split('\n')

                # Get real name
                name_saved = False
                for line in array_full_lines:
                    for real_name in array_name:
                        name_in_line = "Name=" + real_name
                        if line == name_in_line:
                            name = real_name
                            name_saved = True

                    if name_saved:
                        break
            else:
                name = self.functionsClass.exec_command_get_output(cmd)

            if not name:
                name = None

        # Return name App
        return name

    """
        Return all info of desktop files
    """
    def get_desktop_necessary_info(self, desktop_file):
        name = self.get_app_name(desktop_file)
        icon = self.get_icon(desktop_file)
        command = self.get_command(desktop_file)

        return {
            "name": name,
            "icon": icon,
            "command": command
        }

    """
        Create sub menu and return sub menu
    """
    def create_sub_menu(self, sub_menu_data, app_key):
        sub_menu = Gtk.Menu()

        for (key, value) in sub_menu_data.items():
            if key == app_key and value:
                for app in value:
                    if app:
                        info_desktop_file = self.get_desktop_necessary_info(app)
                        if info_desktop_file["name"]:
                            sub_menu_item = Gtk.ImageMenuItem(info_desktop_file["name"])
                            sub_menu_item.set_image(info_desktop_file["icon"])
                            sub_menu_item.set_always_show_image(True)
                            sub_menu_item.connect('activate', self.lauch_desktop, info_desktop_file["command"])
                            sub_menu.append(sub_menu_item)

        # Return sub menu
        return sub_menu

    """
        Create Menu
    """
    def create_menu(self):
        menu = Gtk.Menu()

        key_app = "apps"
        key_separator = "separator_"
        menu = Gtk.Menu()

        for (key, value) in self.json_data.items():
            if key_app == key and value:
                for app in value:
                    info_desktop_file = self.get_desktop_necessary_info(app)
                    if info_desktop_file["name"]:
                        menu_item = Gtk.ImageMenuItem(info_desktop_file["name"])
                        menu_item.set_image(info_desktop_file["icon"])
                        menu_item.set_always_show_image(True)
                        menu_item.connect('activate', self.lauch_desktop, info_desktop_file["command"])
                        menu.append(menu_item)
            elif key_separator in key and value:
                menu_item = Gtk.SeparatorMenuItem()
                menu.append(menu_item)
            else:
                if value:
                    sub_menu_info = self.create_sub_menu(value, key_app)
                    if sub_menu_info:
                        menu_item = Gtk.MenuItem(key)
                        menu_item.set_submenu(sub_menu_info)
                        menu.append(menu_item)

        # Insert Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Insert Exit Menu
        item_exitindicator = Gtk.MenuItem('Exit')
        item_exitindicator.connect('activate', self.exit_indicator)
        menu.append(item_exitindicator)

        # Show Menu and return
        menu.show_all()
        return menu

    """
       Update Menu
    """
    def update_menu(self):
        # Security changes
        count_changes = 0
        max_changes = 20

        # Time to check new change
        time_sleep = 5  # 5 seconds

        # Monitor json file
        while not self.stop_thread:
            info_stats_config_file = self.functionsClass.exec_command_get_output(self.cmd_stat_json_file)
            if info_stats_config_file != self.stats_config_file:
                self.stats_config_file = info_stats_config_file

                # Increment changes count
                count_changes += 1

                # Exit if changes datected greater than max_changes
                if count_changes > max_changes:
                    break

                # Get new json file
                self.json_data = self.read_json_file()

                # update menu
                GObject.idle_add(
                    self.indicator.set_menu,
                    self.create_menu()
                )

            time.sleep(time_sleep)

        if count_changes > max_changes:
            # Notify
            msg = "\"Hit Max changes on JSON File was reached.\n"
            msg = msg + "New changes will be not detected.\n"
            msg = msg + "Please, restart if you want to detect new changes.\""
            self.functionsClass.exec_command(self.zenity_cmd + msg)
            time.sleep(2)
            exit(1)

    """
        Stop thread
    """
    def stop_service(self):
        self.stop_thread = True
        time.sleep(1)

    """
        Start thread for monitor new change on json file and update menu
    """
    def start_service_update_menu(self):
        # Identify functions to run
        thread_update_menu = threading.Thread(target=self.update_menu)

        # Set daemon
        thread_update_menu.daemon = True

        # Start
        thread_update_menu.start()

    """
        Exit
    """
    def exit_indicator(self, source):
        self.stop_service()
        Gtk.main_quit()


FavoritesAppsIndicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
GObject.threads_init()
Gtk.main()
