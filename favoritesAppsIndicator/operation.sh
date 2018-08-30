#!/bin/bash
# Author: José M. C. Noronha

# Args
declare operation="$1"; shift
declare args=("$@")

# Global directory variable
declare home="$(echo $HOME)"
declare appDir="/opt/favoritesAppsIndicator"
declare appConfigDir="$home/.config/favoritesAppsIndicator"
declare autostartDir="$home/.config/autostart"
declare execAppDir="$home/.local/share/applications"

# Kernel files
declare functionsFile="$appDir/functions.sh"
declare operationFile="$appDir/operation.sh"
declare indicator="$appDir/favoritesAppsIndicator.py"

# Config File
declare configFile="$appConfigDir/favoritesApps.json"

# Desktop Files
declare execAppFile="favoritesAppsIndicator.desktop"
declare autostartAppFile="favoritesAppsIndicator.desktop"

# Icons
declare iconDefault="$appDir/icon/favoritesApps.png"

####### FUNCTIONS #######
# Install or uninstall Grive
function installUninstallGrive(){
	local operation="$1"
	local envPath="$(echo $PWD)"

	case "$operation" in
		"install")
		    eval "$installUniGriveFile install"
			;;
		"uninstall")
		    eval "$installUniGriveFile uninstall"
			;;
	esac

	# Go to env path
	cd "$envPath"
}

# Install
function install(){
	echo "Install Grive Indicator..."
	eval "$functionsFile -delFD \"$logTempFile\""

	# Create config dir
	mkdir -p "$appConfigDir"

	# Create config file exameple
	if [ ! -f "$configFile" ]; then
		cp "$appDir/json_example.json" "$configFile"
	fi

	# Create desktop file
	eval "$functionsFile -dFile \"Favorites Apps Indicator\" \"$execAppFile\" \"python3 $indicator\" \"$iconDefault\" 0"
	eval "$functionsFile -dFile \"Favorites Apps Indicator\" \"$execAppFile\" \"python3 $indicator\" \"$iconDefault\" 1"
}

# Uninstall
function uninstall(){
	# Delete desktop files
    eval "$functionsFile -delFD \"$execAppDir/$execAppFile\""
    eval "$functionsFile -delFD \"$autostartDir/$autostartAppFile\""

    # Remove appDir
    eval "$functionsFile -delFD \"$appDir\" 1"
}

# Main
function main(){
    case "$operation" in
		"install")
			install
			;;
		"uninstall")
			uninstall "${args[@]}"
			;;
		*)
			echo ""
			;;
	esac
}
main