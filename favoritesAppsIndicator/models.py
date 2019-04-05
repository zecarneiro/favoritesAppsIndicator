# Author: José M. C. Noronha

import os
from functions import Functions

"""[summary]
    Interface for app
    {
        "desktop": "Name of desktop file",
        "command": "Command to execute app",
        "icon": "Icon to insert",
        "name": "Label to appear on menu"
    }
Returns:
    [type] -- [description]
"""
class AppInfoInterface:
    def __init__(self, app_dir = None, icon_default = None):
        # Init functions class
        self.functions = Functions(app_dir, icon_default)
        self.__sefDefault()

    def __sefDefault(self):
        self.desktop = None
        self.command = None
        self.icon = None
        self.name = None
        self.isDesktop = -1

    def setAppInfo(self, app_info_object):
        self.__sefDefault()
        try:
            if app_info_object["isDesktop"] == 1:
                self.desktop = app_info_object["desktop"]
                self.isDesktop = 1
            elif app_info_object["isDesktop"] == 0:
                self.command = app_info_object["command"]
                self.icon = app_info_object["icon"]
                self.name = app_info_object["name"]
                self.isDesktop = 0
            else:
                self.__sefDefault()
        except Exception as e:
            msg = "\"ERROR on format of app info\""
            self.functions.print_notifications(msg)
            self.functions.set_log('READ JSON', str(e.args))
            self.__sefDefault()

"""[summary]
    Interface for favorites files manager
    {
        "name": "Localizações",
        "filesManagerCmd": "nautilus",
        "bookmarkFile": "$HOME/.config/gtk-3.0/bookmarks",
        "key_in_json: "filesManagerFavorites"
    }
Returns:
    [type] -- [description]
"""
class FavoritesFilesManagerInterface:
    def __init__(self, json_data, app_dir = None, icon_default = None):
        self.name = None
        self.files_manager_cmd = None
        self.bookmark_file = None
        self.object_interface = {}
        self.key_to_replace = "$HOME"
        self.key_in_json = "filesManagerFavorites"
        self.__home_path = os.path.expanduser("~")
        self.__setData()
        self.__getAllData(json_data)

    def __getAllData(self, json_data):
        if self.key_in_json in json_data:
            favoritesConfig = json_data[self.key_in_json]    

            # Get Name
            self.name = favoritesConfig["name"] if "name" in favoritesConfig else self.name

            # Get Files Manager Cmd
            self.files_manager_cmd = favoritesConfig["files_manager_cmd"] if "files_manager_cmd" in favoritesConfig else self.files_manager_cmd

            # Get Bookmark File
            self.bookmark_file = favoritesConfig["bookmarkFile"] if "bookmarkFile" in favoritesConfig else self.bookmark_file
            self.bookmark_file = self.bookmark_file.replace(self.key_to_replace, self.__home_path)

            # Set on object
            self.__setData(False)

            # Delete element
            json_data.pop(self.key_in_json, None)

    def __setData(self, is_default = True):
        if is_default:
            self.name = "Localizações"
            self.files_manager_cmd = "nautilus"
            self.bookmark_file = self.__home_path + "/.config/gtk-3.0/bookmarks"

        self.object_interface = {
            "name": self.name,
            "files_manager_cmd": self.files_manager_cmd,
            "bookmark_file": self.bookmark_file
        }
            


"""[summary]
    Interface for desktop files
    {
        "_system": "/usr/share/applications/",
        "_user": "$HOME/.local/share/applications/",
        "_snaps": "/var/lib/snapd/desktop/applications/",
        "_flatpak": "/var/lib/flatpak/exports/share/applications/",
        "_flatpak_user": "$HOME/.local/share/flatpak/exports/share/applications/"
    }
Returns:
    [type] -- [description]
"""
class DesktopFilesInterface:
    def __init__(self, app_dir = None, icon_default = None):
        self.__homePath = os.path.expanduser("~")
        self.object_interface = {
            "system": "/usr/share/applications/",
            "user": self.__homePath + "/.local/share/applications/",
            "snaps": "/var/lib/snapd/desktop/applications/",
            "flatpak": "/var/lib/flatpak/exports/share/applications/",
            "flatpak_user": self.__homePath + "/.local/share/flatpak/exports/share/applications/"
        }