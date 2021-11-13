from backup import Backup, QMP_SHELL_PATH
from datetime import datetime
import time


class Full(Backup):
    """ Make full backup of a virtual machine """

    def __init__(self, vm_name):
        super().__init__(vm_name)
        self.full_backup_name = 'full-%s.img' % datetime.now().strftime('%Y%m%d%H%M%S')

    def run(self):
        super().validate()

        cmd_full = 'printf "drive-backup device=disk target=%s/%s sync=full format=qcow2" | sudo %s %s' % (
            self.current_backup_path,
            self.full_backup_name,
            QMP_SHELL_PATH,
            self.socket_path
        )

        self.run_command(cmd_full)

        # Every 3 seconds check if the backup is running and update the progress bar
        while self.check_state() is False:
            time.sleep(3)
