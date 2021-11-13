from backup import Backup, QMP_SHELL_PATH
import time


class Incremental(Backup):
    """ Make incremental backup of a virtual machine """

    def __init__(self, vm_name):
        super().__init__(vm_name)
        self.current_inc = 0  # number by which set name of incremental backup
        self.images = self.sort_images()

    def validate(self):
        super().validate()
        super().images_validate()

    def check_last_inc(self):
        """ Set number of current_inc (default: 0) """

        last_inc = self.images[len(self.images) - 1]  # get the latest image

        if 'full-' not in last_inc:
            self.current_inc = last_inc.replace('inc-', '')
            self.current_inc = int(self.current_inc.replace('.img', '')) + 1

    def create_image(self):
        """ Generate image, with backing image, where run incremental backup """

        if self.current_inc == 0:
            backing_image = self.images[0]
        else:
            backing_image = 'inc-%s.img' % str(self.current_inc - 1)

        cmd = 'sudo qemu-img create -f qcow2 %s/inc-%s.img -b %s/%s -F qcow2' % (
            self.current_backup_path,
            self.current_inc,
            self.current_backup_path,
            backing_image
        )

        self.run_command(cmd, False)

    def run(self):
        self.validate()
        self.check_last_inc()
        self.create_image()

        cmd_inc = 'printf "drive-backup device=disk bitmap=bitmap0 target=%s/inc-%s.img format=qcow2 sync=incremental' \
                  ' mode=existing" | sudo %s %s' % (
                      self.current_backup_path,
                      self.current_inc,
                      QMP_SHELL_PATH,
                      self.socket_path
                  )

        self.run_command(cmd_inc)

        # Every 3 seconds check if the backup is running and update the progress bar
        while self.check_state() is False:
            time.sleep(3)
