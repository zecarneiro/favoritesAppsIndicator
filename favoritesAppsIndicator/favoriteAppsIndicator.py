
# Author: José M. C. Noronha

# Include
import signal
import gi
import json
from functions import Functions
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

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

        # Read Json File
        self.json_file = self.configDir + "/favoritesApps.json"
        self.json_data = self.read_json_file()

        # Define Indicator
        self.indicator = AppIndicator3.Indicator.new(
            self.applicationID,
            self.iconDefault,
            AppIndicator3.IndicatorCategory.OTHER
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

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
            exit(1)

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
        print(cmd_to_launch)
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
        Exit
    """
    @staticmethod
    def exit_indicator(source):
        Gtk.main_quit()


FavoritesAppsIndicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
