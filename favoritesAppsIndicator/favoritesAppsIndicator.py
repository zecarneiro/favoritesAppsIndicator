# Author: José M. C. Noronha

# Include
import signal
import gi
import threading
import time
import datetime
import urllib.parse
import os
from models import DesktopFilesInterface, AppInfoInterface, FavoritesFilesManagerInterface
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
        # Set Config files
        self.home = os.path.expanduser("~")
        self.configDir = self.home + "/.config/favoritesAppsIndicator"
        self.iconDefault = APP_DIR + "/icon/favoritesApps.png"

        # Init functions class
        self.functions = Functions(APP_DIR, self.iconDefault)

        # Read Json File
        self.json_file = self.configDir + "/favoritesApps.json"
        self.json_data = self.functions.read_json_file(self.json_file)
        self.cmd_stat_json_file = "stat -c '%y' \"" + self.json_file + "\""
        self.stats_config_file = self.functions.exec_command_get_output(self.cmd_stat_json_file)

        # Init other class
        self.path_desktop_files = DesktopFilesInterface()
        self.favorites_files_manager = FavoritesFilesManagerInterface(self.json_data)
        self.app_info = AppInfoInterface(APP_DIR, self.iconDefault)

        # Other
        self.applicationID = 'favorites_apps_indicator'
        self.stop_thread = False
        self.locale = self.functions.get_locale_code()

        # Keys
        self.key_comment_JsonFile = "INFO"
        self.key_app_no_menu = "EXTERNALAPP"
        self.key_separator = "separator_"

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

    def get_bookmarks_path(self, menu):
        # Create menu localizations and read file
        if self.functions.checkFileExist(self.favorites_files_manager.bookmark_file):
            
            # Create menu localizations
            sub_menu_item = Gtk.MenuItem(self.favorites_files_manager.name)
            sub_menu = Gtk.Menu()
            
            # Read file
            _file = open(self.favorites_files_manager.bookmark_file, 'r')
            lines = list(_file.readlines())
            for line in lines:
                # Get name of Item
                name_item = ""
                array_line = line.split(" ")

                if len(array_line) == 1:
                    array_line_with_len_one = line.split("/")
                    name_item = array_line_with_len_one[-1] # Last element
                else:
                    index = 0
                    for value in array_line:
                        if index == 0:
                            index += 1
                        else:
                            name_item += " " + value
                
                # Insert o menu
                _decode_status = False
                try:
                    name_item = urllib.parse.unquote(name_item)
                    _decode_status = True
                except Exception as e:
                    self.functions.set_log('Error convert url character', str(e.args))

                if not _decode_status:
                    try:
                        name_item = name_item.decode('UTF-8', 'strict')
                        _decode_status = True
                    except Exception as e:
                        self.functions.set_log('Error convert string character', str(e.args))
                
                # Trim character
                name_item = name_item.strip('\t\n\r')
                line = line.strip('\t\n\r')
                array_line[0] = str(array_line[0]).strip('\t\n\r')
                
                # Activate command and insert on menu item
                menu_item = Gtk.MenuItem(name_item)                        
                command_to_menu = self.favorites_files_manager.files_manager_cmd + " \"" + array_line[0] + "\""
                menu_item.connect('activate', self.lauch_desktop, command_to_menu)

                # Insert on sub menu
                sub_menu.append(menu_item)
            
            # Insert sub menu on menu
            sub_menu_item.set_submenu(sub_menu)
            menu.append(sub_menu_item)

            # Close file
            _file.close()  

    """
        Check if Operating System is permited
    """
    def check_permited_operating_system(self):
        not_permited_so_list = [
            'Linux Mint'
        ]
        is_permited = True

        for operating_system in not_permited_so_list:
            command = "lsb_release -a | grep -ci \"" + operating_system + "\""
            result = int(self.functions.exec_command_get_output(command))
            if (result > 0):
                is_permited = False
                break

        # Return result
        return is_permited

    """
        Verify is desktop file exist or not
    """
    def is_desktop_file_exist(self, desktop_file):
        for (key, path) in self.path_desktop_files.object_interface.items():
            if isinstance(path, str):
                file = path + desktop_file
                if self.functions.checkFileExist(file):
                    return file

        # Return false desktop file not exist
        return False

    """
        Launch desktop file
    """
    def lauch_desktop(self, source, command):
        cmd_to_launch = command + " &"
        self.functions.exec_command(cmd_to_launch)

    """
        Return Name by type
        type = 0 - Icon By locale
        type = * - Default Icon
    """
    def get_icon_by_type(self, file=None, type=0):
        icon = ""
        if self.check_permited_operating_system():
            command = None
            if type == 0:
                command = "grep 'Icon[" + self.locale + "]=' \"" + file + "\" | head -1 | cut -d \"=\" -f 2-"
            else:
                command = "grep 'Icon=' \"" + file + "\" | head -1 | cut -d \"=\" -f 2-"

            icon = self.functions.exec_command_get_output(command)

        # Return icon
        return icon

    """
        Return Icon from desktop files
    """
    def get_icon(self, desktop_file_icon, is_icon = False):
        icon = None if not is_icon else desktop_file_icon
        if not is_icon:
            file = self.is_desktop_file_exist(desktop_file_icon)
            if file:
                # Get icon by locale
                icon = self.get_icon_by_type(file)

                # Get default icon
                if not icon or icon == "":
                    icon = self.get_icon_by_type(file, 1)

        # Init Image Gtk
        image = Gtk.Image()

        # Select type of icon
        if self.functions.checkFileExist(icon):
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
            # Check if to run on terminal
            cmd_get_run_on_terminal = "grep 'Terminal=' \"" + file + "\" | cut -d '=' -f 2-"
            is_launch_terminal = self.functions.exec_command_get_output(cmd_get_run_on_terminal)

            # finds the line which starts with Exec
            get_command = "cat \"" + file + "\" | grep 'Exec='"

            # only use the first line, in case there are multiple
            get_command = get_command + " | head -1"

            # removes the Exec= from the start of the line, or get all arg after =
            get_command = get_command + " | cut -d '=' -f 2-"

            # removes any arguments - %u, %f etc
            get_command = get_command + " | sed 's/%.//'"

            # removes " around command (if present) - Activate if necessary
            # get_command = get_command + " | sed 's/^\"//g' | sed 's/\" *$//g'"

            # Get command on desktop file
            command_on_desktop_file = self.functions.exec_command_get_output(get_command)

            # Return command
            if is_launch_terminal == "True" or is_launch_terminal == "true":
                cmd_to_get_default_terminal = "readlink -f $(command -v x-terminal-emulator)"
                default_terminal = self.functions.exec_command_get_output(cmd_to_get_default_terminal)

                return default_terminal + " -e \"" + command_on_desktop_file + "\""
            else:
                return command_on_desktop_file

    """
        Return Name by type
        type = 0 - Name By locale
        type = * - Default Name
    """
    def get_name_by_type(self, file=None, type=0):
        # Remove all line after(include the line) contain "Desktop Action"
        command = "sed -n '/Desktop Action/q;p' \"" + file + "\""

        if type == 0:
            # Get name by locale #
            command = command + " | grep 'Name\[" + self.locale + "\]='"
            command = command + " | grep -v 'Generic'"  # Remove Geniric Names
            command = command + " | cut -d '=' -f 2-"  # Get only name
            command = command + " | head -1"  # only use the first line, in case there are multiple
        else:
            command = command + " | grep 'Name='"
            command = command + " | grep -v 'Generic'"  # Remove Geniric Names
            command = command + " | cut -d '=' -f 2-"  # Get only name
            command = command + " | head -1"  # only use the first line, in case there are multiple

        # Get Name
        name = self.functions.exec_command_get_output(command)

        # Return name
        return name


    """
        Return name app from desktop files
    """
    def get_app_name(self, desktop_file):
        file = self.is_desktop_file_exist(desktop_file)
        name = None
        if file:
            # Get name by locale #
            name = self.get_name_by_type(file)

            # Get Default name if name by locale not set
            if not name or name == "":
                name = self.get_name_by_type(file, 1)

            if not name or name == "":
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

        if name is not None:
            return {
                "name": name,
                "icon": icon,
                "command": command
            }
        else:
            return None

    def insert_items_on_menu_or_sub_menu(self, menu_or_sub_menu, name, command, icon):
        menu_item = Gtk.ImageMenuItem(name)
        menu_item.set_image(icon)
        menu_item.set_always_show_image(True)
        menu_item.connect('activate', self.lauch_desktop, command)
        menu_or_sub_menu.append(menu_item)

    def insert_on_menu(self, menu, list_items):
        # Create Menu or Sub menu
        for value in list_items:
            self.app_info.setAppInfo(value)

            # If is desktop
            if self.app_info.isDesktop == 1:
                info_desktop = self.get_desktop_necessary_info(self.app_info.desktop)
                if info_desktop is not None:
                    self.insert_items_on_menu_or_sub_menu(menu, info_desktop["name"], info_desktop["command"], info_desktop["icon"])
            elif self.app_info.isDesktop == 0:
                self.app_info.icon = self.get_icon(self.app_info.icon, True)
                self.insert_items_on_menu_or_sub_menu(menu, self.app_info.name, self.app_info.command, self.app_info.icon)
                
        
    """
        Insert items on menu and create sub menu if necessary
    """
    def insert_on_sub_menu(self, menu, list_items, name_sub_menu=None):
        # If items for submenus
        if name_sub_menu is not None:
            sub_menu_item = Gtk.MenuItem(name_sub_menu)
            sub_menu = Gtk.Menu()

            # Create Menu or Sub menu
            for value in list_items:
                self.app_info.setAppInfo(value)

                # If is desktop
                if self.app_info.isDesktop == 1:
                    info_desktop = self.get_desktop_necessary_info(self.app_info.desktop)
                    if info_desktop is not None:
                        self.insert_items_on_menu_or_sub_menu(sub_menu, info_desktop["name"], info_desktop["command"], info_desktop["icon"])
                elif self.app_info.isDesktop == 0:
                    self.app_info.icon = self.get_icon(self.app_info.icon, True)
                    self.insert_items_on_menu_or_sub_menu(sub_menu, self.app_info.name, self.app_info.command, self.app_info.icon)

            # If submenu append submenu on menu
            sub_menu_item.set_submenu(sub_menu)
            menu.append(sub_menu_item)
                

    """
        Create Menu
    """
    def create_menu(self):
        menu = Gtk.Menu()
        for (key, value) in self.json_data.items():
            if self.key_comment_JsonFile in key:
                pass
            elif self.key_app_no_menu == key and value:
                self.insert_on_menu(menu, value)
            elif self.key_separator in key and value:
                menu.append(Gtk.SeparatorMenuItem())
            else:
                self.insert_on_sub_menu(menu, value, key)

        # Insert Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Insert bookmarks path
        self.get_bookmarks_path(menu)

        # Insert Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Update Menu
        item_update_menu = Gtk.MenuItem('Update')
        item_update_menu.connect('activate', self.update_menu)
        menu.append(item_update_menu)

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
    def update_menu(self, source):
        # Get new json file
        self.json_data = self.functions.read_json_file(self.json_file)
        self.favorites_files_manager = FavoritesFilesManagerInterface(self.json_data)

        # update menu
        GObject.idle_add(
            self.indicator.set_menu,
            self.create_menu()
        )

        # Update info stats config_file
        info_stats_config_file = self.functions.exec_command_get_output(self.cmd_stat_json_file)
        if info_stats_config_file != self.stats_config_file:
            self.stats_config_file = info_stats_config_file

        # Print notifications
        self.functions.print_notifications("\"Update Favorites Apps Done.\"")

    """
        Service Update Menu
    """
    def thread_update_menu(self):
        # Security changes
        count_changes = 0
        max_changes = 20

        # Time to check new change
        time_sleep = 60  # 1 minute

        # Monitor json file
        while not self.stop_thread:
            info_stats_config_file = self.functions.exec_command_get_output(self.cmd_stat_json_file)
            if info_stats_config_file != self.stats_config_file:
                self.stats_config_file = info_stats_config_file

                # Increment changes count
                count_changes += 1

                # Exit if changes datected greater than max_changes
                if count_changes > max_changes:
                    break

                # Update menu
                self.update_menu(None)

            time.sleep(time_sleep)

        if count_changes > max_changes:
            # Notify
            msg = "\"Hit Max changes on JSON File was reached.\n"
            msg = msg + "New changes will be not detected.\n"
            msg = msg + "Please, restart if you want to detect new changes.\""
            self.functions.print_notifications(msg)
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
        thread_update_menu = threading.Thread(target=self.thread_update_menu)

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
