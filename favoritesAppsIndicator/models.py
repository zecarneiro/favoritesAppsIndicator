# Author: José M. C. Noronha

import os

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
    desktop: str
    command: str
    icon: str
    name: str

    def __init__(self):
        self.desktop = None
        self.command = None
        self.icon = None
        self.name = None

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
    name: str
    files_manager_cmd: str
    bookmark_file: str
    key_to_replace: str
    key_in_json: str
    __home_path: str

    def __init__(self, json_data):
        self.__home_path = os.path.expanduser("~")
        self.name = "Localizações"
        self.files_manager_cmd = "nautilus"
        self.bookmark_file = self.__home_path + "/.config/gtk-3.0/bookmarks"
        self.key_to_replace = "$HOME"
        self.key_in_json = "filesManagerFavorites"
        self.__getAllData(json_data)

    def __getAllData(self, json_data):
        


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
    system_: str
    user_: str
    snaps_: str
    flatpak_: str
    flatpak_user_: str

    """[summary]
        Private variable
    """
    __homePath: str

    def __init__(self):
        self.__homePath = os.path.expanduser("~")
        self.system_ = "/usr/share/applications/"
        self.user_ = self.__homePath + "/.local/share/applications/"
        self.snaps_ = "/var/lib/snapd/desktop/applications/"
        self.flatpak_ = "/var/lib/flatpak/exports/share/applications/"
        self.flatpak_user_ = self.__homePath + "/.local/share/flatpak/exports/share/applications/"