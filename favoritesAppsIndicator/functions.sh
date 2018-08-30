#!/bin/bash
# Author: José M. C. Noronha

# Global variable
declare operation="$1"; shift
declare -a args=("$@")

# Check if installed
function checkIsInstaled(){
    local nameApp="$1"
    if [ ! -z "$(apt-cache policy "$nameApp")" ]; then
        apt-cache policy "$nameApp" | grep -i "instal" | cut -d ":" -f2 | awk '{if ($1 == "(nenhum)" || $1 == "(none)" || $1 == "") {print "0"} else {print "1"}}'
    else
        echo "0"
    fi
}

# Check if ppa exist or not
function checkIsAddedPPA(){
    local ppa="$1"
    local -i existPPA
    local -i response=0
    
    if [ ! -z "$ppa" ]; then
        if [ ! -z "$(echo "$ppa" | cut -d ":" -f2)" ]; then
            ppa="$(echo "$ppa" | cut -d ":" -f2)"
        fi

        existPPA=$(grep "^deb .*$ppa" /etc/apt/sources.list /etc/apt/sources.list.d/* | grep -c .)
        if [ $existPPA -gt 0 ]; then
            response=1
        fi
    fi

    # Return response
    echo "$response"
}

# Check if file or directory exist
function existDirOrFile(){
	local name="$1"
	local -i response

	# Check if is dir
	if [ -d "$name" ]; then
        response=1
    elif [ -f "$name" ]; then
        response=1
    else
        response=0
    fi

	# Return response
	echo $response
}

# Kill app with pid
function killPID(){
	local pid="$1"
	local -i existPID
	local -a subprocessPID=()

	if [ ! -z "$pid" ]; then
		# Check if pid exist
		existPID=$(ps ax | grep $pid | grep -v grep | grep -c .)

		# Kill All PIDs
		if [ $existPID -gt 0 ]; then
		    subprocessPID=( "$(pgrep -P $pid)" )

		    # Kill PID Pai
		    kill $pid 2> /dev/null

		    for PID in "${subprocessPID[@]}"; do
		        if [ ! -z "$PID" ]; then
		            # Check if pid exist
                    existPID=$(ps ax | grep $PID | grep -v grep | grep -c .)

                    # add pid
                    if [ $existPID -gt 0 ]; then
                        # Kill subprocess PID
		                kill $PID 2> /dev/null
                    fi
		        fi
            done
		fi
	fi
}

# Delete File or Dir
function removeFileDir(){
    local name="$1"
    local -i runSudo=$2
    if [ $(existDirOrFile "$name") -eq 1 ]; then
        if [ $runSudo -eq 1 ]; then
            sudo rm -r "$name"
        else
            rm -r "$name"
        fi
    fi
}

# Create/Delete Desktop files
function createDelDesktopFile(){
	local appName="$1"
	local desktopFile="$2"
	local cmdToExec="$3"
	local icon="$4"
	local -i isAutoStart="$5"
    local extraLines="$6"

	local home="$(echo $HOME)"
	local desktopFiletext
	local autoStartApp="$home/.config/autostart"
	local execApp="$home/.local/share/applications"
	local desktopFullPath
	
	if [ $isAutoStart -eq 1 ]; then
	    mkdir -p "$autoStartApp"
	    desktopFullPath="$autoStartApp/$desktopFile"

	    # Auto start indicator
        desktopFiletext="[Desktop Entry]"
        desktopFiletext="$desktopFiletext\nType=Application"
        desktopFiletext="$desktopFiletext\nExec=$cmdToExec"
        desktopFiletext="$desktopFiletext\nIcon=$icon"
        desktopFiletext="$desktopFiletext\nHidden=false"
        desktopFiletext="$desktopFiletext\nNoDisplay=false"
        desktopFiletext="$desktopFiletext\nTerminal=false"
        desktopFiletext="$desktopFiletext\nX-GNOME-Autostart-enabled=true"
        desktopFiletext="$desktopFiletext\nName[pt]=$appName"
        desktopFiletext="$desktopFiletext\nName=$appName"
        desktopFiletext="$desktopFiletext\nComment[pt]="
        desktopFiletext="$desktopFiletext\nComment=\n"
        desktopFiletext="$desktopFiletext\n$extraLines"
        printf "$desktopFiletext" | tee "$desktopFullPath" > /dev/null
        chmod +x "$desktopFullPath"
	else
	    mkdir -p "$execApp"
	    desktopFullPath="$execApp/$desktopFile"

	    # Start indicator
        desktopFiletext="[Desktop Entry]"
        desktopFiletext="$desktopFiletext\nType=Application"
        desktopFiletext="$desktopFiletext\nExec=$cmdToExec"
        desktopFiletext="$desktopFiletext\nIcon=$icon"
        desktopFiletext="$desktopFiletext\nTerminal=false"
        desktopFiletext="$desktopFiletext\nName[pt]=$appName"
        desktopFiletext="$desktopFiletext\nName=$appName"
        desktopFiletext="$desktopFiletext\nGenericName=$appName\n"
        desktopFiletext="$desktopFiletext\n$extraLines"
        printf "$desktopFiletext" | tee "$desktopFullPath" > /dev/null
        chmod +x "$desktopFullPath"
	fi
}

# Execute command and return output
function execCommandGetOutput(){
    local command="$1"
    local response

    response="$(eval "$command")"
    echo "$response"
}

# Install
function install(){
    local -a apps=($1)
    local -a ppa=($2)

    # Set ppa
    for PPA in "${ppa[@]}"; do
        if [ ! -z "$PPA" ]; then
            if [ $(checkIsAddedPPA "$PPA") -eq 0 ]; then
                echo "Set PPA: $PPA..."
                sudo add-apt-repository "$PPA" -y
                sudo apt update
            else
                echo "This $PPA Already Exist..."
            fi
        fi
    done

    # Install
    for APP in "${apps[@]}"; do
        if [ $(checkIsInstaled "$APP") -eq 0 ]; then
            echo "Install $APP..."
            sudo apt install "$APP" -y
        else
            echo "$APP Already Installed..."
        fi
    done
}

# Uninstall
function uninstall(){
    local -a apps=($1)
    local -a ppa=($2)

    # Del ppa
    for PPA in "${ppa[@]}"; do
        if [ ! -z "$PPA" ]; then
            if [ $(checkIsAddedPPA "$PPA") -eq 1 ]; then
                echo "Remove PPA: $PPA..."
                sudo add-apt-repository -r "$PPA" -y
                sudo apt update
            fi
        fi
    done

    # Uninstall
    for APP in "${apps[@]}"; do
        echo "Uninstall $APP..."
        if [ $(checkIsInstaled "$APP") -eq 1 ]; then
            sudo apt purge --auto-remove "$APP" -y
        fi
    done
}

# Main
function main(){
    case "$operation" in
        "-isId")
            checkIsInstaled "${args[@]}"
            ;;
        "-existFD")
            existDirOrFile "${args[@]}"
            ;;
        "-kPID")
            killPID "${args[@]}"
            ;;
        "-delFD")
            removeFileDir "${args[@]}"
            ;;
        "-dFile")
            createDelDesktopFile "${args[@]}"
            ;;
        "-eCmd")
            execCommandGetOutput "${args[@]}"
            ;;
        "-i")
            install "${args[@]}"
            ;;
        "-u")
            uninstall "${args[@]}"
            ;;
        *)
            echo "$0 OPERATION ARGS"
            ;;
    esac
}
main