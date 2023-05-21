from .patch_handler import PatchHandler


class PatchHandlerIps(PatchHandler):
    def prepare_patch(self, rom_file, directory_patch, patch):
        return patch
