#!/bin/bash
# Author: José M. C. Noronha

# print message Init
echo "Install..."

# Global variable
declare nameAppPath="favoritesAppsIndicator"
declare appDir="/opt/$nameAppPath"
declare functionsBashFile="$appDir/functions.sh"
declare operationBashFile="$appDir/operation.sh"

# Copy app
sudo cp -r "$nameAppPath" /opt
sudo chmod -R 755 "$appDir"

# Zenity
eval "$functionsBashFile -i \"zenity python3 python3-gi libappindicator1 libappindicator-dev gir1.2-appindicator3-0.1\""

# Install app
eval "$operationBashFile install"

# print message finish
echo "Done."
exit 0