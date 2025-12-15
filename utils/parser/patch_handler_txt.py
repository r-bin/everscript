from injector import Injector, inject
_injector = Injector()

from utils.file_utils import *
from .patch_handler import PatchHandler
from .patch_handler_ips import PatchHandlerIps


class PatchHandlerTxt(PatchHandler):
    @inject
    def __init__(self, patch_handler_ips: PatchHandlerIps):
        self._patch_handler_ips = patch_handler_ips

    def prepare_patch(self, rom_file, directory_patch, patch, params=[]):
        # print(f" - compiling patch {patch} ({os.path.getsize(patch)})")

        with patch.open() as file_in:
            patch_out = file_in.read()
            patch_out = file_utils.clean(patch_out)

            patch_ips = patch.with_suffix(".ips")

            file_utils.dump(patch_out, patch.with_suffix(".ips"))

            return self._patch_handler_ips.prepare_patch(rom_file, directory_patch, patch_ips)