from injector import Injector, inject
_injector = Injector()

from .parser.patch_handler_asm import *
from .parser.patch_handler_evs import *
from .parser.patch_handler_ips import *
from .parser.patch_handler_sliver import *
from .parser.patch_handler_txt import *

from pathlib import Path
import shutil
import os


class PatchUtils():
    def patch(self, rom_file, patches_in, patches_out, patches):
        self.prepare_patches(rom_file, patches_in, patches_out, patches)

    def prepare_patches(self, rom_file, patches_in, patches_out, patches):
        for patch in patches:
            patch = self._patch_for_name(patches_in, patch)

            copied_patch = os.path.join(patches_out, patch.name)
            copied_patch = Path(copied_patch)
            shutil.copy(patch, copied_patch)

            print(f" - applying patch {patch}", end='')

            patch_handler = None
            match patch.suffix:
                case ".asm":
                    patch_handler = _injector.get(PatchHandlerAsm)
                case ".sliver":
                    patch_handler = _injector.get(PatchHandlerSliver)
                case ".evs":
                    patch_handler = _injector.get(PatchHandlerEvs)
                case ".txt":
                    patch_handler = _injector.get(PatchHandlerTxt)
                case ".ips":
                    patch_handler = _injector.get(PatchHandlerIps)
                case _:
                    raise Exception(f"unknown patch extension for '{patch}'")
                
            patch_out = patch_handler.prepare_patch(rom_file, patches_out, copied_patch)
            
            ips_utils.apply_patch(rom_file, patch_out)

    def _patch_for_name(self, directory_patches, name):
        patch = []

        for file in os.scandir(directory_patches):
            file = Path(file)

            if file.stem == name:
                patch.append(file)

        match len(patch):
            case 0:
                raise Exception(f"no files for patch {name} found ({patch})")
            case 1:
                return patch[0]
            case _:
                raise Exception(f"multiple files for patch {name} found ({patch})")

patch_utils = _injector.get(PatchUtils)