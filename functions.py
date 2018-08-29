# Author: José M. C. Noronha

# Include
import os
import subprocess


class Functions():
    """
        Init
    """
    def __init__(self, app_dir):
        self.functionBashFile = app_dir + "/functions.sh"
        self.openInTerminal = "x-terminal-emulator -e"
    
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
        return os.path.isfile(file)

    """
        Check if directories exists
    """
    def checkDirectoryExist(self, directory):
        return os.path.isdir(directory)