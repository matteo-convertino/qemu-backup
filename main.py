from bitmap import Bitmap
from incremental import Incremental
from rebase import Rebase
from full import Full
import sys


def info():
    print(
        "QEMU-BACKUP accepts these actions:"
        "\n\n- python3 main.py bitmap <VM_NAME>"
        "\n- python3 main.py full <VM_NAME>"
        "\n- python3 main.py inc <VM_NAME>"
        "\n- python3 main.py rebase <VM_NAME>"
        "\n\nFor more information about this project, see github repository https://github.com/matteo-39/qemu-backup"
    )
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        info()

    action = sys.argv[1]
    vm_name = sys.argv[2]
    obj = None

    if action == 'bitmap':
        obj = Bitmap(vm_name)
    elif action == 'full':
        obj = Full(vm_name)
    elif action == 'inc':
        obj = Incremental(vm_name)
    elif action == 'rebase':
        obj = Rebase(vm_name)
    else:
        info()

    obj.run()
