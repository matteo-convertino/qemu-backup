# qemu-backup
This repository has the intention to help you to create and manage your VM's backups. To do this, it uses the [Dirty bitmaps](https://www.qemu.org/docs/master/interop/bitmaps.html) and the [QMP](https://wiki.qemu.org/Documentation/QMP) protocol.

# Prerequisites
Before starting, your VM has to be reachable via QMP through unix socket. This can be done by adding the following option to your command that runs the virtual machine:
```
-qmp unix:/path/vm_name.socket,server,nowait
```
Furthermore, you need [qmp-shell](https://github.com/qemu/qemu/blob/master/scripts/qmp/qmp-shell) because it makes communication via QMP much easier and qemu-backup uses it to run commands and get needed information about VM.

You also have to edit your `-drive` option, because it has to have `id=disk`. It should looks like this:
```
-drive file=/path/file.img,format=qcow2,id=disk
```
Obviously if you want to have another `id` you can, but you have to edit bitmap.py.

# Usage
### config.ini
The first thing you need to do to use qemu-backup is to edit the config.ini file.
```
[DEFAULT]
QmpShellPath = /home/tux/Documents/qemu/scripts/qmp/qmp-shell
SocketPath = /home/tux/Documents/sockets
BackupPath = /media/backups
```
* `QmpShellPath`: you have to enter the path to the [qmp-shell](https://github.com/qemu/qemu/blob/master/scripts/qmp/qmp-shell) file
* `SocketPath`: you have to enter the path to the folder that will contain all unix sockets of VMs for communication via QMP
* `BackupPath`: you have to enter the path that will contain all the backups of the virtual machines.

### bitmap
Then, you can create the bitmap with this command:
```
python3 main.py bitmap <VM_NAME>
```
> :information_source: Basically <VM_NAME> is the name you have given to the socket. It will also be the name that will be given to the folder under `BackupPath`.

Once this command has been run, if you run the following commands you will see something like this:
```
$ printf 'query-block' | sudo /home/tux/Documents/qemu/scripts/qmp/qmp-shell /home/tux/Documents/sockets/mint.socket
Welcome to the QMP low-level shell!
Connected to QEMU 4.2.1

(QEMU) {
    "return": 
        ... 
        "dirty-bitmaps": [{"name": "bitmap0", "recording": true, "persistent": true, "busy": false, "status": "active", "granularity": 65536, "count": 1900806144}], 
        ... 
}
```
```
$ tree /media/backups
/media/backups/
├── mint
│   ├── current
│   └── old
```

### full
Now, you are ready to run the first full backup for your virtual machine. So, run the following command:
```
python3 main.py full <VM_NAME>
```
You should see a progress bar that displays the backup completion with the remaining bytes and, when it has finished, the path where the backup was saved:
```
$ python3 main.py full mint
Running full backup |#######...........................................| 0 of 10737418240 bytes

Backup completed
Path: "/media/backups/mint/current/full-20211109171941.img"
```

### inc
After full backup, you can perform the incremental backup whenever you like with this command:
```
python3 main.py inc <VM_NAME>
```
As for full backup, you should see an output like this:
```
$ python3 main.py inc mint
Running incremental backup |#######...........................................| 0 of 1073741824 bytes

Backup completed
Path: "/media/backups/mint/current/inc-0.img"
```

### rebase
The rebase action allows you to restore all saved changes inside your incremental backups to the single full backup in the current folder. This way you have an image ready to boot, but if you don't need to make another full backup you can continue to use that image for the other incremental backups. For example, I run a rebase every 10 incremental backups.
```
$ python3 main.py rebase mint
"/media/backups/mint/current/full-20211112175452.img" is based on "/media/backups/mint/current/inc-0.img"
sudo qemu-img check /media/backups/mint/current/inc-0.img
sudo qemu-img rebase -b "/media/backups/mint/current/full-20211112175452.img" "/media/backups/mint/current/inc-0.img"
sudo qemu-img commit "/media/backups/mint/current/inc-0.img"
sudo rm /media/backups/mint/current/inc-0.img

Rollback of latest [FULL]<-[INC] chain complete
```

## Other scripts
In addition to those python scripts, I developed two other scripts in bash to perform backups before shutting down the virtual machine.

### run_backup.sh
This script is placed directly on the virtual machine. To execute it, I created a shortcut on the desktop that runs the script in a terminal. If you want, you can have the command run automatically before shutdown but I don't recommend it because, for example, if you make any changes that don't boot up the VM anymore, you take them with you in the backups. So I prefer to run them manually with a double click.

### run_from_vm.sh
This script is the one that is executed by run_backup.sh, so it is placed on the host, basically with the other python scripts. After performing the backup, it sends a shutdown to the virtual machine.
