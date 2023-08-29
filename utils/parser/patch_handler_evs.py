from injector import Injector, inject
_injector = Injector()

from utils.file_utils import *
from .patch_handler import PatchHandler
from .patch_handler_txt import PatchHandlerTxt
from utils.arg_utils import *
from utils.process_utils import *

import shutil

class PatchHandlerEvs(PatchHandler):
    @inject
    def __init__(self, patch_handler_txt: PatchHandlerTxt):
        self._patch_handler_txt = patch_handler_txt

    def prepare_patch(self, rom_file, directory_patch, patch):
        # print(f" - compiling patch {patch} to {patch.with_suffix('.txt').name} ({os.path.getsize(patch)})")

        with patch.open() as f:
            p = f.read()
            p = file_utils.clean(p)

            args = arg_utils.parse()

            # print(f" - compiling patch {patch.name} to {patch.with_suffix('.txt').name}")
            call_args = [args.executable, f"./everscript.py", f"--asm={args.asm}", f"--out=./{args.output_dir}/patches/{patch.stem}/", f"{patch}"]
            process_utils.call(call_args, True)

            patch_from = f"./{args.output_dir}/patches/{patch.stem}/patch.txt"
            patch_to = patch.with_suffix('.txt')
            shutil.copy(patch_from, patch_to)

            return self._patch_handler_txt.prepare_patch(rom_file, directory_patch, patch_to)