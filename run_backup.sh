#!/bin/bash

function zenity_ask { zenity --question --text "It's time to run a '$1' action. Do you want to run it" --no-wrap --ok-label "Yes" --cancel-label "No, I will run incremental"; }
function zenity_notify { zenity --notification --text="$1"; }
function run_ssh_cmd { sshpass -p 96779677 ssh matteo@192.168.25.83 "$1"; }

# Check if host is reachable before continue
if ! run_ssh_cmd "whoami";
then
  zenity --error --title "Error" --text "The host is unreachable. Can't run backup!" --width=300 --height=100
  exit
fi

day_of_month=$(date '+%d')

if [ "$day_of_month" -eq 1 ] && zenity_ask "re-full" # if it's the first of the month, ask if you want to run a re-full (rebase & full)
then
  zenity_notify "Re-full action started. It will take a few minutes."
  run_ssh_cmd "/home/matteo/vm/vm_backup_scripts/run_from_vm.sh rebase mint && sudo mv /media/backup_vm/mint/current/full-*.img /media/backup_vm/mint/old/ && /home/matteo/vm/vm_backup_scripts/run_from_vm.sh full mint"
elif run_ssh_cmd "find /media/backup_vm/mint/current/inc-10.img" && zenity_ask "rebase"; # if there are 10 incremental backups, ask if you want to run a rebase
then
  zenity_notify "Rebase action started"
  run_ssh_cmd "/home/matteo/vm/vm_backup_scripts/run_from_vm.sh inc,rebase mint"
else # by default it runs an incremental backup
  zenity_notify "Incremental backup started"
  run_ssh_cmd "/home/matteo/vm/vm_backup_scripts/run_from_vm.sh inc mint"
fi
