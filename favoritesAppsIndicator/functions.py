# Author: José M. C. Noronha

# Include
import os
import subprocess
import json
import datetime

# Print json data: print(json.dumps(self.json_data, indent=4, sort_keys=True))

class Functions:
    """
        Init
    """
    def __init__(self, app_dir, icon):
        self.homePath = os.path.expanduser("~")
        self.functionBashFile = app_dir + "/functions.sh"
        self.openInTerminal = "x-terminal-emulator -e"
        self.zenity_cmd = "zenity --notification --window-icon=\"" + icon + "\" --text="
    
    """
        Only execute command
    """
    def exec_command(self, command):
        os.system(command)

    """
        Execute command and return output
    """
    def exec_command_get_output(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        (output, error) = process.communicate()
        return output.decode("utf-8").strip("\n")

    """
        Check if app is instaled or not
    """
    def check_is_instaled(self, app_name):
        command = self.functionBashFile + " -isId " + app_name
        if self.exec_command_get_output(command) == 1:
            return True
        else:
            return False
    
    """
        Check if files exists
    """
    def checkFileExist(self, file):
        if isinstance(file, str):
            return os.path.isfile(file)
        else:
            return False

    """
        Check if directories exists
    """
    def checkDirectoryExist(self, directory):
        return os.path.isdir(directory)

    """
        Get Locale
    """
    def get_locale_code(self):
        cmd_locale = "locale | grep LANGUAGE | cut -d= -f2- | cut -d ':' -f1"
        return self.exec_command_get_output(cmd_locale)

    """
        Read JSON File
    """
    def read_json_file(self, json_file):
        json_data = {}
        try:
            stream = open(json_file, 'r')
            json_data = json.load(stream)
            stream.close()
        except Exception as e:
            msg = "\"ERROR on read JSON File\""
            self.print_notifications(msg)
            self.set_log('READ JSON', str(e.args))
            json_data = {}
        return json_data

    """
        Print notifications
    """
    def print_notifications(self, message = ''):
        self.exec_command(self.zenity_cmd + message)

    """
        [Set Log Error]
    """
    def set_log(self, _type, _error_log):
        _type = _type + " " + str(datetime.datetime.now())
        localization_log_file = self.homePath + "/.favoritesAppsIndicatorLog.log"
        command = "echo \"" + _type + ": " + _error_log + "\" | tee -a " + localization_log_file + " > /dev/null"
        self.exec_command(command)

    def print_json_data(self, json_data):
        print(json.dumps(json_data, indent=4, sort_keys=True))

    def checkKey(self, object, key):
        if key in object.keys(): 
            return True
        else: 
            return False