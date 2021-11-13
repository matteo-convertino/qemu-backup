from backup import Backup, QMP_SHELL_PATH


class Bitmap(Backup):
    """ Generate a persistent bitmap for VM """

    def __init__(self, vm_name):
        super().__init__(vm_name)

    def create_folders(self):
        cmd_current_folder = 'sudo mkdir -p %s' % self.current_backup_path
        cmd_old_folder = 'sudo mkdir -p %s' % self.old_backup_path

        self.run_command(cmd_current_folder, False)
        self.run_command(cmd_old_folder, False)

    def run(self):
        self.create_folders()
        super().validate()

        cmd_bitmap = 'printf "block-dirty-bitmap-add node=disk name=bitmap0 persistent=true" | sudo %s %s' % (
            QMP_SHELL_PATH,
            self.socket_path
        )

        self.run_command(cmd_bitmap)
