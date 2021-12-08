from backup import Backup


class Rebase(Backup):
    """ Rebase and commit all images inside VM's full backup """

    def __init__(self, vm_name):
        super().__init__(vm_name)
        self.images = self.sort_images()

    def validate(self):
        super().images_validate()

        if "full" in self.images[-1]:
            self.error('Error: No incremental images found, nothing to commit')

    def run(self):
        self.validate()

        idx = len(self.images) - 1
        for image in reversed(self.images):
            idx = idx - 1
            if self.images.index(image) == 0 or 'full' in image:
                print('Rollback of latest [FULL]<-[INC] chain complete\n')
                break

            print('"%s/%s" is based on "%s/%s"' % (
                self.current_backup_path,
                self.images[idx],
                self.current_backup_path,
                image
            ))

            # before rebase we check consistency of file
            cmd_check = 'sudo qemu-img check %s/%s' % (
                self.current_backup_path,
                image
            )
            print(cmd_check)
            self.run_command(cmd_check, False)

            cmd_rebase = 'sudo qemu-img rebase -b "%s/%s" "%s/%s"' % (  # -u
                self.current_backup_path,
                self.images[idx],
                self.current_backup_path,
                image,
            )
            print(cmd_rebase)
            self.run_command(cmd_rebase, False)

            cmd_commit = 'sudo qemu-img commit "%s/%s"' % (
                self.current_backup_path,
                image
            )
            print(cmd_commit)
            self.run_command(cmd_commit, False)

            cmd_remove = 'sudo rm %s/%s' % (
                self.current_backup_path,
                image
            )
            print(cmd_remove + '\n')
            self.run_command(cmd_remove, False)
