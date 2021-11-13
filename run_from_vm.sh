#!/bin/bash

function send_shutdown { sshpass -p 96779677 ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" matteo@192.168.25.84 "$1"; }

cd /home/matteo/vm/vm_backup_scripts/ || exit

# split actions by ',' to array
IFS=',' read -ra actions <<< "$1"

# run every actions
for action in "${actions[@]}"; do sudo python3 -u main.py "$action" "$2" || exit; done

if [ "$2" == "mint" ]
then
  send_shutdown "sudo systemctl hibernate"
elif [ "$2" == "win10" ]
then
  send_shutdown "shutdown /s /t 0"
fi
