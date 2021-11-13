from glob import glob
from progress.bar import Bar
import json
import os
import configparser
import subprocess

config = configparser.ConfigParser()
config.read('%s/config.ini' % os.getcwd())

QMP_SHELL_PATH = config['DEFAULT']['QmpShellPath'] if not config['DEFAULT']['QmpShellPath'].endswith('/') else config['DEFAULT']['QmpShellPath'][:-1]
SOCKET_PATH = config['DEFAULT']['SocketPath'] if not config['DEFAULT']['SocketPath'].endswith('/') else config['DEFAULT']['SocketPath'][:-1]
BACKUP_PATH = config['DEFAULT']['BackupPath'] if not config['DEFAULT']['BackupPath'].endswith('/') else config['DEFAULT']['BackupPath'][:-1]


class Backup:
    """ Super class for backup. It has the main attributes and methods """

    def __init__(self, vm_name):
        self.vm_name = vm_name
        self.socket_path = '%s/%s.socket' % (
            SOCKET_PATH,
            vm_name
        )
        self.current_backup_path = '%s/%s/current' % (
            BACKUP_PATH,
            vm_name
        )
        self.old_backup_path = '%s/%s/old' % (
            BACKUP_PATH,
            vm_name
        )
        self.pb = Bar(
            # self.__class__.__name__ returns which subclass calls this method
            'Running full backup' if self.__class__.__name__ == "Full" else 'Running incremental backup',
            empty_fill=".",
            suffix="%(index)d of %(max)d bytes"
        )

    @staticmethod
    def error(text):
        print(text)
        exit(1)

    @staticmethod
    def check_cmd_output(cmd_output):
        """ Check if the QMP command has returned an error """

        cmd_output = cmd_output.decode("utf-8")  # bytes --> string
        cmd_output = cmd_output.split("\n")  # split lines inside string to array

        error = None
        for line in cmd_output:
            if "error" in line:
                line = line[line.find('{'):]  # remove all before {'error': {'desc': '...'}}
                error = json.loads(line)['error']['desc']  # get only the description of the error
                break

        return error

    def validate(self):
        """ Check if there are the backup folders and the VM's socket """

        if not os.path.exists(self.current_backup_path):
            self.error('Error: Unable to find directory "%s"' % self.current_backup_path)

        if not os.path.exists(self.old_backup_path):
            self.error('Error: Unable to find directory "%s"' % self.old_backup_path)

        if not os.path.exists(self.socket_path):
            self.error('Error: Unable to find VM\'s socket "%s"' % self.socket_path)

    def images_validate(self):
        """ Check if the images inside the current backup folder are as they should """

        if len(self.images) == 0:
            self.error('Error: No image files found in "%s"' % self.current_backup_path)

        if "full" not in self.images[0]:
            self.error('Error: First image file is not a full backup')

    def run_command(self, cmd, check=True):
        """ Run command and check the output if 'check' is True.
            The commands that will be checked are those via QMP protocol. """

        try:
            output = subprocess.check_output(cmd, shell=True)
            if check:
                error = self.check_cmd_output(output)
                if error:
                    raise subprocess.CalledProcessError(1, cmd, error)
        except subprocess.CalledProcessError as e:
            self.error('Error: %s\n%s' % (e.output, e))

    def check_state(self):
        """ Check the state of the backup process """

        cmd = 'printf "info block-jobs" | sudo %s -H %s' % (
            QMP_SHELL_PATH,
            self.socket_path
        )
        output = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Check if the backup is still running
        if 'No active jobs' not in output:
            # Format to get only the current and max value to print on the progress bar.
            # example: "Type backup, device disk: Completed 8739028992 of 107374182400 bytes, speed limit 0 bytes/s"
            # --> ["8739028992", "107374182400"]
            values = output.split('Completed', 1)[1]
            values = values.split('bytes', 1)[0]
            values = values.split('of')

            self.pb.max = int(values[1])

            # The value passed to the 'next' method represents how much it has to add to old value (self.pb.index)
            self.pb.next(int(values[0]) - self.pb.index)

            return False
        else:
            self.pb.next(self.pb.max - self.pb.index)
            self.pb.finish()

            print('\nBackup completed\nPath: "%s/%s"' % (
                self.current_backup_path,
                # self.__class__.__name__ returns which subclass calls this method
                self.full_backup_name if self.__class__.__name__ == "Full" else 'inc-%s.img' % self.current_inc
            ))

            return True

    def sort_images(self):
        """ Return the images inside current backup folder sorted by date """

        full_backup_image = [os.path.basename(image) for image in glob('%s/full*.img' % self.current_backup_path)]

        # multiple full backups inside the current folder can be a problem when run 'inc' or 'rebase'
        if len(full_backup_image) > 1:
            self.error('Error: There are multiple full backups inside "%s". Please move or delete the '
                       'unnecessary backup' % self.current_backup_path)

        inc_backup_images = [os.path.basename(image) for image in glob('%s/inc*.img' % self.current_backup_path)]

        images = full_backup_image + inc_backup_images
        images.sort(key=lambda image: os.path.getmtime('%s/%s' % (
            self.current_backup_path,
            image
        )))

        return images
