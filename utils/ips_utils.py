from injector import Injector, inject
_injector = Injector()

from utils.file_utils import *

from ips_util import Patch
import os
from os.path import exists


class IpsUtils():
    def create_rom_diff(self, file_in, file_out, file_patch):
        patch = None
        with open(file_in, 'rb') as f_in:
            with open(file_out, 'rb') as f_out:
                patch = Patch.create(f_in.read(), f_out.read())

                with open(file_patch, 'w+b') as f_patch:
                    f_patch.write(patch.encode())

    def apply_patch(self, file, patch):
        file = Path(file)
        patch = Path(patch)

        patch_records = Patch.load(patch)
        patch_size = os.path.getsize(patch)

        print(f" ({patch_size})")

        file_tmp = file_utils.tmp_file_name(file)
        file_utils.safe_delete(file_tmp)

        os.rename(file, file_tmp)

        with open(file_tmp, 'rb') as f_in:
            with open(file, 'w+b') as f_out:
                f_out.write(patch_records.apply(f_in.read()))

        file_utils.safe_delete(file_tmp)


ips_utils = _injector.get(IpsUtils)