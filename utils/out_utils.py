from injector import Injector, inject
_injector = Injector()

from .arg_utils import *
from .file_utils import *
from .object_utils import *
from .ips_utils import *
from .patch_utils import *
from .string_utils import *

import pathlib
import shutil
import os, subprocess
from os.path import exists
import shutil
import binascii
from textwrap import wrap
from pathlib import Path


class OutUtils():
    _out = "./out"
    _tmp = os.path.join(_out, "tmp")
    _patches = os.path.join(_out, "patches")

    def __init__(self):
        args = arg_utils.parse()

        self._out = args.output_dir
        self._tmp = os.path.join(self._out, "tmp")
        self._patches = os.path.join(self._out, "patches")

    def init_out(self):
        self.clean_out()

        Path(self._out).mkdir(parents=True, exist_ok=True)
        Path(self._tmp).mkdir(parents=True, exist_ok=True)
        Path(self._patches).mkdir(parents=True, exist_ok=True)

    def clean_out(self):        
        if os.path.exists(self._out) and os.path.isdir(self._out):
            shutil.rmtree(self._out)
        os.mkdir(self._out)

    def dump(self, text, file):
        file = os.path.join(self._out, file)

        file_utils.dump(text, file)

        return file

    def prepare_rom(self, file):
        if file != None:
            file = Path(file)
            
            target_name = os.path.join(self._out, file.name)
            target_name = Path(target_name)
            shutil.copyfile(file, target_name)

            file_utils.prepare_rom(target_name)

    def prepare_patches(self, rom_file, directory_in, patches):
        if rom_file != None:
            rom_file = os.path.join(self._out, rom_file)
            rom_file = Path(rom_file)

        patch_utils.patch(rom_file, directory_in, self._patches, patches)

    def patch(self, file_in, patch):
        file_in = Path(file_in)
        file_size = os.path.getsize(file_in)

        file_patch = Path(patch)

        print(f" - patching '{file_in}' ({file_size}) + '{file_patch.name}'", end='')

        target_name = os.path.join(self._out, file_in)
        
        ips_utils.apply_patch(target_name, file_patch)

        diff = os.path.join(self._out, "everscript.combined.ips")
        print(f" - creating diff '{diff}'…")
        ips_utils.create_rom_diff(file_in, target_name, diff)

        print(f" - patched successfully! {file_in.name} ({file_size}) + {file_patch.name} ({os.path.getsize(file_patch)}) -> {target_name} ({os.path.getsize(target_name)})")


out_utils = _injector.get(OutUtils)