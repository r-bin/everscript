from injector import Injector, inject
_injector = Injector()

from .patch_handler import PatchHandler
from .patch_handler_ips import PatchHandlerIps
from utils.ips_utils import *
from utils.arg_utils import *
from utils.process_utils import *

import os, subprocess
from subprocess import call
import pathlib
import shutil


class PatchHandlerAsm(PatchHandler):
    @inject
    def __init__(self, patch_handler_ips: PatchHandlerIps):
        self._patch_handler_ips = patch_handler_ips

    def prepare_patch(self, rom_file, directory_patch, patch):
        # print(f" - compiling patch {patch} ({os.path.getsize(patch)})")

        tmp_rom = os.path.join(directory_patch, patch.stem)
        tmp_rom = Path(tmp_rom)
        tmp_rom = tmp_rom.with_suffix('.sfc')
        shutil.copy(rom_file, tmp_rom)

        args = arg_utils.parse()

        process_utils.call([args.asm, patch, tmp_rom], True)

        diff = os.path.join(directory_patch, patch.stem)
        diff = Path(tmp_rom)
        diff = tmp_rom.with_suffix('.ips')
        ips_utils.create_rom_diff(rom_file, tmp_rom, diff)

        return self._patch_handler_ips.prepare_patch(rom_file, directory_patch, diff)